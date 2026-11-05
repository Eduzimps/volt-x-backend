"""Independent local installations; this module does not alter account access.

Each profile has private configuration, queue, history and mutable resources.
Only static application resources and the frozen runtime may use hard links.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unicodedata
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener
import uuid


MARKER = ".pyla-profile.json"
RUNTIME = ".pyla-profile-runtime.json"
INSTANCE_LOCK = ".pyla-profile-instance.lock"
_PROFILE_ID = re.compile(r"[0-9a-f]{32}\Z")
_WEBHOOK_SECRETS = frozenset({
    "webhook_url", "discord_id", "telegram_token", "telegram_chat_id",
    "discord_bot_token", "discord_guild_id",
})
_HISTORY_HEADER = (
    "date_time,brawler_name,result,current_trophies,trophy_delta,new_winstreak,"
    "playstyle_hash,playstyle_name,playstyle_gamemodes,playstyle_brawlers,"
    "pyla_version,power_level\n"
)


def _atomic_json(path, data):
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class _FileLock:
    """Small OS lock shared by threads, app processes and profile children."""

    def __init__(self, path):
        self.path = Path(path)
        self.handle = None

    def acquire(self, blocking=True):
        self.handle = self.path.open("a+b")
        try:
            if os.name == "nt":
                import msvcrt
                self.handle.seek(0, os.SEEK_END)
                if self.handle.tell() == 0:
                    self.handle.write(b"\0")
                    self.handle.flush()
                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_LOCK if blocking else msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
        except OSError:
            self.handle.close()
            self.handle = None
            if blocking:
                raise
            return False
        return True

    def release(self):
        if self.handle is None:
            return
        try:
            if os.name == "nt":
                import msvcrt
                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        finally:
            self.handle.close()
            self.handle = None


def _profile_id(value):
    if not isinstance(value, str) or not _PROFILE_ID.fullmatch(value):
        raise ValueError("Invalid profile ID.")
    return value


def _profile_name(value):
    if not isinstance(value, str):
        raise ValueError("Profile name must be text.")
    name = value.strip()
    if (not name or len(name) > 80 or name in {".", ".."}
            or any(char in '/\\<>:"|?*' or unicodedata.category(char).startswith("C") for char in name)):
        raise ValueError("Use a profile name of 1–80 characters without path separators or control characters.")
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-") or "profile"
    return name, slug


def _link_or_copy(source, destination):
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)
    return destination


def _copy_tree(source, destination, *, immutable=False):
    """Copy an explicit resource tree, rejecting links that leave the install."""
    source = Path(source)
    source_root = source.resolve()
    for path in source.rglob("*"):
        if path.is_symlink() or not path.resolve().is_relative_to(source_root):
            raise ValueError(f"Resource trees must not contain symbolic links: {path.name}")
    shutil.copytree(source, destination, copy_function=_link_or_copy if immutable else shutil.copy2,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def _pid_alive(pid):
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return False
    if os.name == "nt":
        # os.kill(pid, 0) uses TerminateProcess on Windows; never probe with it.
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel32.GetExitCodeProcess.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        process = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not process:
            return ctypes.get_last_error() == 5  # Access denied still means a PID exists.
        try:
            code = wintypes.DWORD()
            return bool(kernel32.GetExitCodeProcess(process, ctypes.byref(code))) and code.value == 259
        finally:
            kernel32.CloseHandle(process)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _local_url(value):
    try:
        parsed = urlsplit(str(value))
        if (parsed.scheme == "http" and parsed.hostname == "127.0.0.1"
                and parsed.port and not parsed.username and not parsed.password
                and parsed.path in {"", "/"} and not parsed.query and not parsed.fragment):
            return f"http://127.0.0.1:{parsed.port}"
    except ValueError:
        pass
    return None


def _url_ready(url, token):
    try:
        # Local UI probes must never use an inherited HTTP proxy.
        with build_opener(ProxyHandler({})).open(url, timeout=0.3) as response:
            return response.status == 200 and response.headers.get("X-Pyla-Profile-Token") == token
    except (OSError, ValueError):
        return False


class _UITokenParser(HTMLParser):
    token = None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "meta" and values.get("name") == "pyla-ui-token":
            self.token = values.get("content")


def _stop_runtime(url, instance_token, timeout):
    """Ask the owned child to stop, and confirm the bot thread has finished."""
    if not url:
        raise ValueError("Profile UI is not ready; leave it running and stop it from its own window.")
    deadline = time.monotonic() + timeout
    opener = build_opener(ProxyHandler({}))

    def fetch(path="", *, ui_token=None, method="GET"):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError("Profile is still stopping; its process has been left running.")
        headers = {"X-Pyla-UI-Token": ui_token} if ui_token else {}
        request = Request(url + path, headers=headers, method=method)
        with opener.open(request, timeout=min(2.5, remaining)) as response:
            if response.headers.get("X-Pyla-Profile-Token") != instance_token:
                raise ValueError("Could not identify the profile UI; its process has been left running.")
            return response.read(4 * 1024 * 1024).decode("utf-8", errors="replace")

    try:
        parser = _UITokenParser()
        parser.feed(fetch())
        if not parser.token:
            raise ValueError("Could not read the profile UI session; its process has been left running.")
        result = json.loads(fetch("/api/runtime/stop", ui_token=parser.token, method="POST"))
        while True:
            runtime = result.get("runtime", {})
            if runtime.get("is_running") is False:
                return
            if time.monotonic() >= deadline:
                raise ValueError("Profile is still stopping; its process has been left running.")
            time.sleep(min(0.1, max(0, deadline - time.monotonic())))
            result = json.loads(fetch("/api/runtime/status", ui_token=parser.token))
    except (OSError, TypeError, AttributeError, json.JSONDecodeError) as error:
        raise ValueError("Could not confirm that the bot stopped; its process has been left running.") from error


class ProfileManager:
    def __init__(self, root, *, frozen=None, executable=None, popen_factory=None):
        self.root = Path(root).resolve()
        self.directory = self.root / "profiles"
        self.registry = self.directory / "registry.json"
        self.enabled = not (self.root / MARKER).exists()
        self.frozen = bool(getattr(sys, "frozen", False)) if frozen is None else bool(frozen)
        # Preserve virtualenv symlinks: resolving python loses its environment.
        self.executable = Path(executable or sys.executable).absolute()
        self._popen = popen_factory or subprocess.Popen
        self._processes = {}
        self._thread_lock = threading.RLock()

    def _require_enabled(self):
        if not self.enabled:
            raise ValueError("Manage profiles from the main installation, not from a profile window.")

    @contextmanager
    def _locked_registry(self):
        self._require_enabled()
        with self._thread_lock:
            if self.directory.is_symlink():
                raise ValueError("The profiles directory must not be a symbolic link.")
            self.directory.mkdir(exist_ok=True)
            if self.directory.resolve().parent != self.root:
                raise ValueError("The profiles directory escapes the main installation.")
            lock = _FileLock(self.directory / ".registry.lock")
            lock.acquire()
            try:
                if self.registry.exists():
                    data = json.loads(self.registry.read_text(encoding="utf-8"))
                    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("profiles"), list):
                        raise ValueError("Invalid local profile registry.")
                else:
                    data = {"version": 1, "profiles": []}
                yield data
            finally:
                lock.release()

    def _path(self, profile_id):
        path = self.directory / _profile_id(profile_id)
        if path.is_symlink() or path.resolve().parent != self.directory.resolve():
            raise ValueError("Profile path escapes its installation.")
        return path

    def _entry(self, data, profile_id):
        _profile_id(profile_id)
        for entry in data["profiles"]:
            if isinstance(entry, dict) and entry.get("id") == profile_id:
                self._path(profile_id)
                return entry
        raise ValueError("Profile not found.")

    def _running(self, entry):
        process = self._processes.get(entry["id"])
        if process is not None:
            if process.poll() is None:
                return True
            self._processes.pop(entry["id"], None)
        path = self._path(entry["id"])
        if not path.is_dir():
            return False
        lock = _FileLock(path / INSTANCE_LOCK)
        if not lock.acquire(blocking=False):
            return True
        lock.release()
        # Cover the short interval between Popen and the child's first import.
        return time.time() - float(entry.get("launched_at", 0)) < 30 and _pid_alive(entry.get("pid"))

    def _view(self, entry, *, probe=False):
        path = self._path(entry["id"])
        running = self._running(entry)
        url = None
        runtime_pid = None
        if running:
            try:
                runtime = json.loads((path / RUNTIME).read_text(encoding="utf-8"))
                # Windows virtualenv launchers may spawn a second Python PID.
                # Bind readiness to the random launch token and HTTP identity,
                # not equality with the wrapper process identifier.
                if runtime.get("token") == entry.get("launch_token") and isinstance(runtime.get("pid"), int) and runtime["pid"] > 0:
                    url = _local_url(runtime.get("url"))
                    runtime_pid = runtime["pid"]
            except (OSError, ValueError, TypeError):
                pass
        return {"id": entry["id"], "name": entry["name"], "slug": entry.get("slug", "profile"),
                "created_at": entry["created_at"], "path": str(path), "running": running,
                "pid": entry.get("pid") if running else None, "runtime_pid": runtime_pid, "url": url,
                "ready": bool(url and probe and _url_ready(url, entry.get("launch_token")))}

    def list_profiles(self):
        if not self.enabled:
            return []
        with self._locked_registry() as data:
            return [self._view(entry) for entry in data["profiles"]]

    def get(self, profile_id):
        with self._locked_registry() as data:
            return self._view(self._entry(data, profile_id), probe=True)

    def create(self, name):
        name, slug = _profile_name(name)
        with self._locked_registry() as data:
            if any(entry["name"].casefold() == name.casefold() for entry in data["profiles"]):
                raise ValueError("A profile with this name already exists.")
            profile_id = uuid.uuid4().hex
            destination = self._path(profile_id)
            destination.mkdir()
            try:
                # Explicit allowlist prevents recursive profiles, logs or audit data.
                _copy_tree(self.root / "cfg", destination / "cfg")
                for resource in ("models", "playstyles", "api", "scrcpy"):
                    if (self.root / resource).is_dir():
                        _copy_tree(self.root / resource, destination / resource)
                for resource in ("templates", "static", "images"):
                    if (self.root / resource).is_dir():
                        _copy_tree(self.root / resource, destination / resource, immutable=True)
                if self.frozen:
                    if self.executable.parent.parent != self.root:
                        raise ValueError("Frozen executable must be inside the installation's internal directory.")
                    _copy_tree(self.executable.parent, destination / self.executable.parent.name, immutable=True)
                elif not (self.root / "main.py").is_file():
                    raise ValueError("The main source entry point was not found.")
                if (self.root / "LICENSE").is_file():
                    shutil.copy2(self.root / "LICENSE", destination / "LICENSE")
                import toml
                webhook_path = destination / "cfg" / "webhook_config.toml"
                if webhook_path.is_file():
                    webhook = toml.loads(webhook_path.read_text(encoding="utf-8"))
                    for key in _WEBHOOK_SECRETS & webhook.keys():
                        webhook[key] = ""
                    webhook_path.write_text(toml.dumps(webhook), encoding="utf-8")
                (destination / "latest_brawler_data.json").write_text("[]\n", encoding="utf-8")
                (destination / "cfg" / "match_history.csv").write_text(_HISTORY_HEADER, encoding="utf-8")
                entry = {"id": profile_id, "name": name, "slug": slug,
                         "created_at": datetime.now(timezone.utc).isoformat()}
                _atomic_json(destination / MARKER, {**entry, "version": 1, "source_root": str(self.root)})
                data["profiles"].append(entry)
                _atomic_json(self.registry, data)
            except BaseException:
                shutil.rmtree(destination)
                raise
            return self._view(entry)

    def launch(self, profile_id, *, interface_mode="browser", readiness_timeout=0.0):
        if interface_mode not in {"browser", "headless", "desktop"}:
            raise ValueError("Invalid profile interface mode.")
        readiness_timeout = max(0.0, min(float(readiness_timeout), 30.0))
        with self._locked_registry() as data:
            entry = self._entry(data, profile_id)
            if not self._running(entry):
                path = self._path(profile_id)
                if not (path / MARKER).is_file():
                    raise ValueError("Profile installation is missing its metadata.")
                token = uuid.uuid4().hex
                if self.frozen:
                    command = [str(path / self.executable.parent.name / self.executable.name)]
                else:
                    command = [str(self.executable), str(self.root / "main.py")]
                flag = {"browser": "--web", "headless": "--headless", "desktop": "--desktop"}[interface_mode]
                command += ["--profile-root", str(path), "--profile-child", "--profile-token", token, flag]
                process_options = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW}
                                   if os.name == "nt" else {"start_new_session": True})
                with (path / "pyla-profile.log").open("ab") as log:
                    process = self._popen(command, cwd=str(path), stdin=subprocess.DEVNULL,
                                          stdout=log, stderr=subprocess.STDOUT, shell=False, close_fds=True,
                                          **process_options)
                self._processes[profile_id] = process
                entry.update(pid=process.pid, launch_token=token, launched_at=time.time())
                try:
                    _atomic_json(self.registry, data)
                except BaseException:
                    process.terminate()
                    raise
        deadline = time.monotonic() + readiness_timeout
        while True:
            result = self.get(profile_id)
            if result["ready"] or not result["running"] or time.monotonic() >= deadline:
                return result
            time.sleep(min(0.1, max(0, deadline - time.monotonic())))

    def stop(self, profile_id, *, timeout=5.0):
        """Stop only a child launched by this manager, never an arbitrary PID."""
        self._require_enabled()
        _profile_id(profile_id)
        with self._thread_lock:
            process = self._processes.get(profile_id)
            if process is None:
                raise ValueError("This application did not launch that profile process.")
            if process.poll() is None:
                with self._locked_registry() as data:
                    entry = self._entry(data, profile_id)
                    view = self._view(entry)
                    token = entry.get("launch_token")
                try:
                    _stop_runtime(view["url"], token, max(0.1, min(float(timeout), 5.0)))
                except ValueError:
                    if process.poll() is None:
                        raise
                    return self.get(profile_id)
                if os.name == "nt" and view.get("runtime_pid") not in (None, process.pid):
                    # Stop a Windows Python redirector and its owned interpreter
                    # together, only after the authenticated bot stop completed.
                    subprocess.run([str(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "taskkill.exe"),
                                    "/PID", str(process.pid), "/T", "/F"],
                                   check=True, timeout=10, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
        return self.get(profile_id)


class ProfileInstance:
    """Keep the instance lock alive until the child process exits."""

    def __init__(self, root, token):
        self.root = root
        self.token = token
        self.lock = _FileLock(root / INSTANCE_LOCK)
        if not self.lock.acquire(blocking=False):
            raise ValueError("This profile already has a running instance.")
        try:
            _atomic_json(root / RUNTIME, {"pid": os.getpid(), "token": token, "url": None})
        except BaseException:
            self.lock.release()
            raise

    def publish_url(self, url):
        valid_url = _local_url(url)
        if valid_url is None:
            raise ValueError("Invalid local profile URL.")
        _atomic_json(self.root / RUNTIME, {"pid": os.getpid(), "token": self.token, "url": valid_url})

    def close(self):
        self.lock.release()


def bootstrap_profile(root=None, *, child=False, token=None, frozen=None, executable=None):
    """Select cwd and lock a profile before utils or the application is imported."""
    frozen = bool(getattr(sys, "frozen", False)) if frozen is None else bool(frozen)
    executable = Path(executable or sys.executable).resolve()
    candidate = Path(root).resolve() if root else (executable.parent.parent if frozen else Path.cwd().resolve())
    marker_path = candidate / MARKER
    if not marker_path.is_file():
        if root is not None or child:
            raise ValueError("The requested directory is not a local profile installation.")
        return None
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    if marker.get("version") != 1 or _profile_id(marker.get("id")) != candidate.name:
        raise ValueError("Invalid profile metadata.")
    if frozen and executable.parent.parent != candidate:
        raise ValueError("Launch the executable inside this profile's internal directory.")
    instance = ProfileInstance(candidate, token or uuid.uuid4().hex)
    os.chdir(candidate)
    return instance
