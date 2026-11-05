"""Player snapshots use only explicit local data or the public official API."""

import json

import pytest
import requests

from player_data import OfficialBrawlStarsClient, PlayerDataError, PlayerDataService


@pytest.fixture(autouse=True)
def prohibit_external_requests(monkeypatch):
    def forbidden_request(*args, **kwargs):
        raise AssertionError("Player-data tests must never contact an external service")
    monkeypatch.setattr(requests.sessions.Session, "request", forbidden_request)


def official_player(**updates):
    payload = {
        "tag": "#2PP",
        "name": "Local player",
        "brawlers": [
            {"name": "MR. P", "trophies": 123, "power": 8, "winStreak": 2},
            {"name": "8-BIT", "trophies": 0},
            {"name": "LARRY & LAWRIE", "power": 3},
        ],
    }
    payload.update(updates)
    return payload


def service(tmp_path, **kwargs):
    return PlayerDataService(
        tmp_path,
        brawler_catalog=["Mr. P", "8-Bit", "Larry&Lawrie"],
        **kwargs,
    )


def test_official_json_import_maps_catalog_and_preserves_absent_fields(tmp_path, monkeypatch):
    monkeypatch.delenv("BRAWL_STARS_API_TOKEN", raising=False)
    data = service(tmp_path)
    payload = data.import_snapshot(official_player())
    assert payload["ok"] is True
    assert payload["player_tag"] == "2PP"
    assert payload["player_name"] == "Local player"
    assert payload["stats"] == {
        "Mr. P": {"trophies": 123, "power_level": 8, "win_streak": 2},
        "8-Bit": {"trophies": 0},
        "Larry&Lawrie": {"power_level": 3},
    }
    assert payload["source"] == "imported"
    assert payload["snapshot_at"]
    assert payload["snapshot_age_seconds"] >= 0
    assert payload["credential_available"] is False
    assert data.load() is not None
    assert (tmp_path / "player-data.json").is_file()
    restored = service(tmp_path).get("#2PP")
    assert restored["ok"] is True
    assert restored["stats"] == payload["stats"]
    assert restored["source"] == "imported"


@pytest.mark.parametrize("encoding", ["object", "text", "bytes"])
def test_local_format_import_accepts_object_or_json(tmp_path, encoding):
    local = {
        "player_tag": "%232pp",
        "player_name": "Local format",
        "stats": {"MR. P": {"trophies": 7, "power": 1, "win_streak": 0}},
    }
    payload = local if encoding == "object" else json.dumps(local)
    if encoding == "bytes":
        payload = payload.encode("utf-8")
    result = service(tmp_path).import_snapshot(payload)
    assert result["ok"] is True
    assert result["player_tag"] == "2PP"
    assert result["stats"]["Mr. P"] == {"trophies": 7, "power_level": 1, "win_streak": 0}


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        "{bad json",
        b"\xff",
        {"name": "Missing tag", "brawlers": []},
        {"tag": "#2PP", "brawlers": []},
        {"tag": "#2PP", "name": "", "brawlers": []},
        official_player(brawlers="invalid"),
        official_player(brawlers=["invalid"]),
        official_player(brawlers=[{"name": "MR. P", "trophies": -1}]),
        official_player(brawlers=[{"name": "MR. P", "trophies": True}]),
        official_player(brawlers=[{"name": "MR. P", "power": 1.5}]),
        official_player(snapshot_at="0001-01-01T00:00:00+23:00"),
    ],
)
def test_invalid_import_preserves_previous_snapshot(tmp_path, payload):
    data = service(tmp_path)
    data.import_snapshot(official_player())
    path = tmp_path / "player-data.json"
    before = path.read_bytes()
    with pytest.raises(ValueError):
        data.import_snapshot(payload)
    assert path.read_bytes() == before
    assert data.get()["player_name"] == "Local player"


@pytest.mark.parametrize("tag", ["#", "ABC", "2P", "2PP/../../", "2PP?x=y", "##2PP", "2PP#", "2PP\n2PP"])
def test_malformed_tags_rejected_before_any_network(tmp_path, monkeypatch, tag):
    monkeypatch.setenv("BRAWL_STARS_API_TOKEN", "test-token-never-send")
    data = service(tmp_path)
    with pytest.raises(ValueError):
        data.import_snapshot(official_player(tag=tag))
    result = data.get(tag, refresh=True)
    assert result["ok"] is False
    assert result["code"] == "INVALID_PLAYER_TAG"
    assert result["stats"] == {}


def test_missing_credential_is_explicit_and_never_invents_statistics(tmp_path, monkeypatch):
    monkeypatch.delenv("BRAWL_STARS_API_TOKEN", raising=False)
    result = service(tmp_path).get("#2PP", refresh=True)
    assert result["ok"] is False
    assert result["code"] == "MISSING_CREDENTIAL"
    assert result["credential_available"] is False
    assert result["stats"] == {}


def test_cached_snapshot_needs_no_api_credential(tmp_path, monkeypatch):
    monkeypatch.delenv("BRAWL_STARS_API_TOKEN", raising=False)
    data = service(tmp_path)
    data.import_snapshot(official_player())
    assert data.get("2PP")["ok"] is True
    refreshed = data.get("2PP", refresh=True)
    assert refreshed["ok"] is False
    assert refreshed["code"] == "MISSING_CREDENTIAL"
    assert data.get("2PP")["ok"] is True


def test_profiles_keep_separate_snapshots(tmp_path):
    first = service(tmp_path / "first")
    second = service(tmp_path / "second")
    first.import_snapshot(official_player(name="First"))
    second.import_snapshot(official_player(name="Second", tag="#2PY"))
    assert first.get()["player_name"] == "First"
    assert second.get()["player_name"] == "Second"
    assert (tmp_path / "first" / "player-data.json").is_file()
    assert (tmp_path / "second" / "player-data.json").is_file()


def test_corrupt_persisted_snapshot_does_not_become_fake_player_data(tmp_path, monkeypatch):
    monkeypatch.delenv("BRAWL_STARS_API_TOKEN", raising=False)
    (tmp_path / "player-data.json").write_text("{invalid", encoding="utf-8")
    result = service(tmp_path).get("2PP")
    assert result["ok"] is False
    assert result["stats"] == {}


class FakeResponse:
    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self.body = json.dumps(official_player()).encode() if body is None else body
        self.closed = False

    def iter_content(self, chunk_size):
        yield self.body

    def close(self):
        self.closed = True


class FakeSession:
    def __init__(self, response=None, error=None):
        self.response = response or FakeResponse()
        self.error = error
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if self.error:
            raise self.error
        return self.response


def test_official_request_is_fixed_host_tls_verified_and_bounded(monkeypatch):
    monkeypatch.setenv("BRAWL_STARS_API_TOKEN", "test-secret-never-output")
    session = FakeSession()
    result = OfficialBrawlStarsClient(session=session).fetch_player("#2pp")
    assert result["name"] == "Local player"
    assert len(session.calls) == 1
    url, options = session.calls[0]
    assert url == "https://api.brawlstars.com/v1/players/%232PP"
    assert options["headers"]["Authorization"] == "Bearer test-secret-never-output"
    assert options["timeout"] == (5, 15)
    assert options["verify"] is True
    assert options["allow_redirects"] is False
    assert options["stream"] is True
    assert session.response.closed is True


def test_official_bearer_auth_ignores_netrc_and_session_credentials(monkeypatch):
    monkeypatch.setenv("BRAWL_STARS_API_TOKEN", "test-env-token-only")
    fake_session = FakeSession()
    OfficialBrawlStarsClient(session=fake_session).fetch_player("2PP")
    url, options = fake_session.calls[0]

    def forbidden_netrc(*args, **kwargs):
        raise AssertionError("Official API must use only the configured token")

    monkeypatch.setattr(requests.sessions, "get_netrc_auth", forbidden_netrc)
    session = requests.Session()
    session.auth = ("unrelated-user", "unrelated-credential")
    prepared = session.prepare_request(requests.Request(
        "GET", url, headers=options["headers"], auth=options["auth"],
    ))
    assert prepared.headers["Authorization"] == "Bearer test-env-token-only"


def test_missing_official_credential_does_not_request(monkeypatch):
    monkeypatch.delenv("BRAWL_STARS_API_TOKEN", raising=False)
    session = FakeSession()
    client = OfficialBrawlStarsClient(session=session)
    assert client.credential_available is False
    with pytest.raises(PlayerDataError) as caught:
        client.fetch_player("2PP")
    assert caught.value.code == "MISSING_CREDENTIAL"
    assert session.calls == []


@pytest.mark.parametrize(
    ("status", "code"),
    [
        (301, "API_UNAVAILABLE"),
        (401, "API_CREDENTIAL_REJECTED"),
        (403, "API_CREDENTIAL_REJECTED"),
        (404, "PLAYER_NOT_FOUND"),
        (429, "API_RATE_LIMITED"),
        (500, "API_UNAVAILABLE"),
    ],
)
def test_upstream_status_errors_never_echo_response_or_secret(tmp_path, monkeypatch, caplog, status, code):
    secret = "test-redaction-secret"
    monkeypatch.setenv("BRAWL_STARS_API_TOKEN", secret)
    response = FakeResponse(status, body=("private upstream details " + secret).encode())
    data = service(tmp_path, client=OfficialBrawlStarsClient(session=FakeSession(response)))
    result = data.get("2PP", refresh=True)
    assert result["ok"] is False
    assert result["code"] == code
    assert result["stats"] == {}
    assert secret not in json.dumps(result)
    assert "private upstream details" not in json.dumps(result)
    assert secret not in caplog.text
    assert response.closed is True
    assert not (tmp_path / "player-data.json").exists()


def test_upstream_network_exception_is_redacted(tmp_path, monkeypatch, caplog):
    secret = "test-network-secret"
    monkeypatch.setenv("BRAWL_STARS_API_TOKEN", secret)
    session = FakeSession(error=requests.ConnectionError("Authorization: Bearer " + secret))
    result = service(tmp_path, client=OfficialBrawlStarsClient(session=session)).get("2PP", refresh=True)
    assert result["ok"] is False
    assert result["code"] == "API_NETWORK_ERROR"
    assert secret not in json.dumps(result)
    assert secret not in caplog.text


@pytest.mark.parametrize("body", [b"{bad json", b"[]", b"null", b"x" * (2 * 1024 * 1024 + 1)])
def test_invalid_upstream_response_is_rejected(monkeypatch, body):
    monkeypatch.setenv("BRAWL_STARS_API_TOKEN", "test-secret")
    response = FakeResponse(body=body)
    with pytest.raises(PlayerDataError) as caught:
        OfficialBrawlStarsClient(session=FakeSession(response)).fetch_player("2PP")
    assert caught.value.code == "API_INVALID_RESPONSE"
    assert response.closed is True


def test_refresh_persists_official_snapshot_for_later_offline_use(tmp_path, monkeypatch):
    monkeypatch.setenv("BRAWL_STARS_API_TOKEN", "test-secret")
    session = FakeSession()
    result = service(tmp_path, client=OfficialBrawlStarsClient(session=session)).get("2PP", refresh=True)
    assert result["ok"] is True
    assert result["source"] == "official"
    monkeypatch.delenv("BRAWL_STARS_API_TOKEN")
    cached = service(tmp_path).get("#2PP")
    assert cached["ok"] is True
    assert cached["source"] == "official"
    assert cached["stats"] == result["stats"]
    assert cached["credential_available"] is False


def test_snapshot_for_different_tag_is_not_reused(tmp_path, monkeypatch):
    monkeypatch.delenv("BRAWL_STARS_API_TOKEN", raising=False)
    data = service(tmp_path)
    data.import_snapshot(official_player())
    other = data.get("2PY")
    assert other["ok"] is False
    assert other["code"] == "MISSING_CREDENTIAL"
    assert other["stats"] == {}


def test_import_marks_local_origin_and_discards_unrelated_fields(tmp_path):
    raw = official_player()
    raw.update({"source": "official", "api_token": "do-not-save-this", "premium": True})
    result = service(tmp_path).import_snapshot(raw)
    assert result["source"] == "imported"
    saved = (tmp_path / "player-data.json").read_text(encoding="utf-8")
    assert "do-not-save-this" not in saved
    assert "api_token" not in saved
    assert "premium" not in saved


def test_local_snapshot_timestamp_reports_age(tmp_path):
    raw = {
        "player_tag": "2PP",
        "player_name": "Historic snapshot",
        "stats": {"MR. P": {"trophies": 1}},
        "snapshot_at": "2020-01-01T00:00:00+00:00",
    }
    result = service(tmp_path).import_snapshot(raw)
    assert result["snapshot_age_seconds"] > 24 * 60 * 60
    assert result["snapshot_at"].startswith("2020-01-01")


@pytest.mark.parametrize("source", [None, [], {}, 5, "unknown"])
def test_malformed_saved_source_is_reported_safely(tmp_path, source):
    data = service(tmp_path)
    data.import_snapshot(official_player())
    path = tmp_path / "player-data.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["source"] = source
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(PlayerDataError) as caught:
        data.load()
    assert caught.value.code == "INVALID_SNAPSHOT"
    result = data.get("2PP")
    assert result["ok"] is False
    assert result["code"] == "INVALID_SNAPSHOT"
    assert result["stats"] == {}


def test_failed_atomic_replace_preserves_previous_snapshot(tmp_path, monkeypatch):
    import player_data
    data = service(tmp_path)
    data.import_snapshot(official_player())
    path = tmp_path / "player-data.json"
    before = path.read_bytes()

    def fail_replace(*args, **kwargs):
        raise OSError("simulated atomic replace failure")

    monkeypatch.setattr(player_data.os, "replace", fail_replace)
    with pytest.raises(OSError):
        data.import_snapshot(official_player(name="New data"))
    assert path.read_bytes() == before
    assert list(tmp_path.glob(".player-data-*.tmp")) == []
