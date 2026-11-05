"""Independent player snapshots from local JSON or the official Brawl Stars API.

Local JSON uses ``player_tag``, ``player_name`` and a ``stats`` object keyed by
brawler name. Each brawler may supply integer ``trophies``, ``power_level`` (or
``power``) and ``win_streak``. An optional timezone-aware ``snapshot_at`` ISO
timestamp preserves the age of an older export. Official API player objects
with ``tag``, ``name`` and ``brawlers`` are also accepted. Missing statistics
remain absent; importing data does not grant authentication or premium access.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile
import threading
from typing import Any

import requests

from utils import normalize_brawler_filename


MAX_SNAPSHOT_BYTES = 2 * 1024 * 1024
_TAG_PATTERN = re.compile(r"[0289PYLQGRJCUV]{3,15}\Z")
_API_PLAYER_URL = "https://api.brawlstars.com/v1/players/%23"


class _BearerAuth(requests.auth.AuthBase):
    """Explicit auth prevents requests from substituting credentials from netrc."""

    def __init__(self, token: str):
        self._token = token

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        request.headers["Authorization"] = "Bearer " + self._token
        return request


class PlayerDataError(ValueError):
    """A safe error whose message never includes an upstream body or credential."""

    def __init__(self, code: str, message: str, http_status: int | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status = http_status


def normalize_player_tag(value: Any) -> str:
    """Return an uppercase tag without its optional leading # or %23."""
    if not isinstance(value, str):
        raise PlayerDataError("INVALID_PLAYER_TAG", "Enter a valid Brawl Stars player tag.")
    value = value.strip().upper()
    if value.startswith("%23"):
        value = value[3:]
    elif value.startswith("#"):
        value = value[1:]
    if not _TAG_PATTERN.fullmatch(value):
        raise PlayerDataError("INVALID_PLAYER_TAG", "Enter a valid Brawl Stars player tag.")
    return value


class OfficialBrawlStarsClient:
    """Only the official, fixed HTTPS host is used; API tokens stay in memory."""

    def __init__(self, session: Any = None):
        self._session = session if session is not None else requests.Session()

    @property
    def credential_available(self) -> bool:
        return bool(os.environ.get("BRAWL_STARS_API_TOKEN", "").strip())

    def fetch_player(self, player_tag: str) -> dict[str, Any]:
        tag = normalize_player_tag(player_tag)
        token = os.environ.get("BRAWL_STARS_API_TOKEN", "").strip()
        if not token:
            raise PlayerDataError(
                "MISSING_CREDENTIAL",
                "Official API credential is missing. Set BRAWL_STARS_API_TOKEN or import a local player JSON file.",
            )

        response = None
        try:
            response = self._session.get(
                _API_PLAYER_URL + tag,
                headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
                auth=_BearerAuth(token),
                timeout=(5, 15),
                verify=True,
                allow_redirects=False,
                stream=True,
            )
            status = response.status_code
            if status in (401, 403):
                raise PlayerDataError(
                    "API_CREDENTIAL_REJECTED",
                    "The official API rejected the credential or its allowed IP address.",
                    status,
                )
            if status == 404:
                raise PlayerDataError("PLAYER_NOT_FOUND", "The official API could not find this player tag.", status)
            if status == 429:
                raise PlayerDataError("API_RATE_LIMITED", "The official API rate limit was reached. Try again later.", status)
            if status != 200:
                raise PlayerDataError("API_UNAVAILABLE", "The official API is unavailable. Try again later.", status)

            chunks: list[bytes] = []
            size = 0
            for chunk in response.iter_content(chunk_size=65536):
                if not chunk:
                    continue
                size += len(chunk)
                if size > MAX_SNAPSHOT_BYTES:
                    raise PlayerDataError("API_INVALID_RESPONSE", "The official API returned an invalid player response.")
                chunks.append(chunk)
            try:
                payload = json.loads(b"".join(chunks).decode("utf-8-sig"))
            except (ValueError, UnicodeError, RecursionError):
                raise PlayerDataError("API_INVALID_RESPONSE", "The official API returned an invalid player response.") from None
            if not isinstance(payload, dict):
                raise PlayerDataError("API_INVALID_RESPONSE", "The official API returned an invalid player response.")
            return payload
        except requests.RequestException:
            # Request exceptions may contain headers, proxy credentials or bodies.
            raise PlayerDataError("API_NETWORK_ERROR", "Could not connect to the official API. Try again later.") from None
        finally:
            if response is not None:
                response.close()


def _parse_json(payload: Any) -> dict[str, Any]:
    if isinstance(payload, (str, bytes)):
        if len(payload.encode("utf-8") if isinstance(payload, str) else payload) > MAX_SNAPSHOT_BYTES:
            raise PlayerDataError("INVALID_SNAPSHOT", "Player JSON must be at most 2 MiB.")
        try:
            payload = json.loads(payload)
        except (ValueError, UnicodeError, RecursionError):
            raise PlayerDataError("INVALID_SNAPSHOT", "Player data must contain valid JSON.") from None
    if not isinstance(payload, dict):
        raise PlayerDataError("INVALID_SNAPSHOT", "Player data must be a JSON object.")
    return payload


def _nonempty_name(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 128:
        raise PlayerDataError("INVALID_SNAPSHOT", f"Player JSON requires a valid {label}.")
    return value.strip()


def _stats_fields(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        raise PlayerDataError("INVALID_SNAPSHOT", "Each brawler must be a JSON object.")
    result: dict[str, int] = {}
    for target, aliases in (
        ("trophies", ("trophies",)),
        ("power_level", ("power_level", "power")),
        ("win_streak", ("win_streak", "winStreak")),
    ):
        for field in aliases:
            if field not in value or value[field] is None:
                continue
            number = value[field]
            if isinstance(number, bool) or not isinstance(number, int) or number < 0:
                raise PlayerDataError("INVALID_SNAPSHOT", "Brawler statistics must be nonnegative integers.")
            if target in result and result[target] != number:
                raise PlayerDataError("INVALID_SNAPSHOT", "Brawler statistics contain conflicting values.")
            result[target] = number
    return result


def _snapshot_time(value: Any = None) -> str:
    if value is None:
        moment = datetime.now(timezone.utc)
    else:
        if not isinstance(value, str):
            raise PlayerDataError("INVALID_SNAPSHOT", "snapshot_at must be an ISO timestamp with a timezone.")
        try:
            moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise PlayerDataError("INVALID_SNAPSHOT", "snapshot_at must be an ISO timestamp with a timezone.") from None
        if moment.tzinfo is None:
            raise PlayerDataError("INVALID_SNAPSHOT", "snapshot_at must include a timezone.")
    try:
        return moment.astimezone(timezone.utc).isoformat(timespec="seconds")
    except (ValueError, OverflowError):
        raise PlayerDataError("INVALID_SNAPSHOT", "snapshot_at must be a valid ISO timestamp with a timezone.") from None


def _normalize_snapshot(payload: Any, source: str) -> dict[str, Any]:
    payload = _parse_json(payload)
    official_shape = "brawlers" in payload
    local_shape = "stats" in payload
    if official_shape == local_shape:
        raise PlayerDataError("INVALID_SNAPSHOT", "Player JSON needs either a brawlers array or a stats object.")
    tag = normalize_player_tag(payload.get("tag") if official_shape else payload.get("player_tag"))
    name = _nonempty_name(payload.get("name") if official_shape else payload.get("player_name"), "player name")
    stats: dict[str, dict[str, int]] = {}
    normalized_names: set[str] = set()
    if official_shape:
        brawlers = payload["brawlers"]
        if not isinstance(brawlers, list):
            raise PlayerDataError("INVALID_SNAPSHOT", "brawlers must be an array.")
        entries = []
        for brawler in brawlers:
            if not isinstance(brawler, dict):
                raise PlayerDataError("INVALID_SNAPSHOT", "Each brawler must be a JSON object.")
            entries.append((brawler.get("name"), brawler))
    else:
        if not isinstance(payload["stats"], dict):
            raise PlayerDataError("INVALID_SNAPSHOT", "stats must be a JSON object.")
        entries = payload["stats"].items()
    for raw_name, values in entries:
        brawler_name = _nonempty_name(raw_name, "brawler name")
        key = normalize_brawler_filename(brawler_name)
        if not key or key in normalized_names:
            raise PlayerDataError("INVALID_SNAPSHOT", "Brawler names must be unique.")
        normalized_names.add(key)
        stats[brawler_name] = _stats_fields(values)
    return {
        "schema_version": 1,
        "player_tag": tag,
        "player_name": name,
        "stats": stats,
        "source": source,
        "snapshot_at": _snapshot_time(payload.get("snapshot_at")),
    }


class PlayerDataService:
    """Read or replace one profile's snapshot; network refresh is always explicit."""

    def __init__(
        self,
        profile_root: str | Path,
        brawler_catalog: Iterable[str] | Callable[[], Iterable[str]] = (),
        client: OfficialBrawlStarsClient | None = None,
    ):
        self.path = Path(profile_root) / "player-data.json"
        self._catalog = brawler_catalog
        self._client = client if client is not None else OfficialBrawlStarsClient()
        self._lock = threading.RLock()

    @property
    def credential_available(self) -> bool:
        return self._client.credential_available

    def _payload(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        catalog = self._catalog() if callable(self._catalog) else self._catalog
        catalog_names = {normalize_brawler_filename(name): name for name in catalog}
        stats = {
            catalog_names.get(normalize_brawler_filename(name), name): dict(values)
            for name, values in snapshot["stats"].items()
        }
        moment = datetime.fromisoformat(snapshot["snapshot_at"])
        return {
            "ok": True,
            "player_tag": snapshot["player_tag"],
            "player_name": snapshot["player_name"],
            "stats": stats,
            "source": snapshot["source"],
            "snapshot_at": snapshot["snapshot_at"],
            "snapshot_age_seconds": max(0, int((datetime.now(timezone.utc) - moment).total_seconds())),
            "credential_available": self.credential_available,
        }

    def _error_payload(self, error: PlayerDataError, tag: str = "", snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
        result = dict(snapshot) if snapshot else {
            "player_tag": tag,
            "player_name": "",
            "stats": {},
            "source": None,
            "snapshot_at": None,
            "snapshot_age_seconds": None,
            "credential_available": self.credential_available,
        }
        result.update(ok=False, code=error.code, message=error.message)
        if snapshot:
            result["stale"] = True
        return result

    def load(self) -> dict[str, Any] | None:
        """Return a validated saved payload, or None; never contacts the network."""
        with self._lock:
            try:
                with self.path.open("rb") as handle:
                    payload = _parse_json(handle.read(MAX_SNAPSHOT_BYTES + 1))
            except FileNotFoundError:
                return None
            source = payload.get("source")
            if (
                not isinstance(source, str)
                or source not in {"imported", "official"}
                or type(payload.get("schema_version")) is not int
                or payload["schema_version"] != 1
            ):
                raise PlayerDataError("INVALID_SNAPSHOT", "The saved player snapshot has an invalid format.")
            if not payload.get("snapshot_at"):
                raise PlayerDataError("INVALID_SNAPSHOT", "The saved player snapshot is missing its timestamp.")
            return self._payload(_normalize_snapshot(payload, source=source))

    def _save(self, snapshot: dict[str, Any]) -> None:
        text = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
        if len(text.encode("utf-8")) > MAX_SNAPSHOT_BYTES:
            raise PlayerDataError("INVALID_SNAPSHOT", "Player JSON must be at most 2 MiB.")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.path.parent,
                prefix=".player-data-", suffix=".tmp", delete=False,
            ) as handle:
                temporary_path = Path(handle.name)
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, self.path)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def import_snapshot(self, payload: Any) -> dict[str, Any]:
        """Validate supported JSON and atomically persist it as imported data."""
        with self._lock:
            snapshot = _normalize_snapshot(payload, source="imported")
            self._save(snapshot)
            return self._payload(snapshot)

    def get(self, player_tag: str | None = None, refresh: bool = False) -> dict[str, Any]:
        """Use saved data unless a caller explicitly requests an official refresh."""
        with self._lock:
            try:
                tag = normalize_player_tag(player_tag) if player_tag is not None and player_tag != "" else ""
            except PlayerDataError as error:
                return self._error_payload(error)
            try:
                saved = self.load()
            except PlayerDataError as error:
                if not refresh:
                    return self._error_payload(error, tag)
                saved = None
            matching = saved if saved and (not tag or saved["player_tag"] == tag) else None
            if not refresh:
                if matching:
                    return matching
                if not self.credential_available:
                    error = PlayerDataError(
                        "MISSING_CREDENTIAL",
                        "Official API credential is missing. Set BRAWL_STARS_API_TOKEN or import a local player JSON file.",
                    )
                else:
                    error = PlayerDataError("NO_PLAYER_DATA", "No player snapshot is saved. Refresh from the official API or import local JSON.")
                return self._error_payload(error, tag)
            tag = tag or (saved["player_tag"] if saved else "")
            if not tag:
                return self._error_payload(PlayerDataError("INVALID_PLAYER_TAG", "Enter a valid Brawl Stars player tag."))
            try:
                raw = self._client.fetch_player(tag)
                try:
                    snapshot = _normalize_snapshot(raw, source="official")
                    if snapshot["player_tag"] != tag:
                        raise ValueError
                except ValueError:
                    raise PlayerDataError("API_INVALID_RESPONSE", "The official API returned an invalid player response.") from None
                self._save(snapshot)
                return self._payload(snapshot)
            except PlayerDataError as error:
                return self._error_payload(error, tag, matching)
