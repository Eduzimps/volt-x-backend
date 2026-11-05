from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.request import ProxyHandler, build_opener

import pytest
import toml

import profiles
from profiles import ProfileManager, bootstrap_profile


PROJECT = Path(__file__).resolve().parents[1]


@pytest.fixture
def installation(tmp_path):
    root = tmp_path / "installation"
    root.mkdir()
    (root / "cfg").mkdir()
    (root / "cfg" / "general_config.toml").write_text('max_fps = "60"\n', encoding="utf-8")
    (root / "cfg" / "login.toml").write_text('key = "existing-account-key"\n', encoding="utf-8")
    (root / "cfg" / "webhook_config.toml").write_text(
        'webhook_url = "https://example.invalid/private"\n'
        'discord_bot_token = "private-token"\ntelegram_token = "private-telegram"\n'
        'telegram_chat_id = "123"\nping_when_stuck = true\n', encoding="utf-8")
    (root / "cfg" / "match_history.csv").write_text("header\nprivate history\n", encoding="utf-8")
    for name in ("models", "playstyles", "api", "scrcpy", "static", "templates", "images"):
        (root / name).mkdir()
        (root / name / "resource.bin").write_bytes(b"original resource")
    (root / "latest_brawler_data.json").write_text('[{"brawler":"Shelly"}]', encoding="utf-8")
    (root / "LICENSE").write_text("upstream license\n", encoding="utf-8")
    # A small real child proves process/bootstrap/HTTP readiness without loading
    # emulators, inference runtimes or the third-party account service.
    (root / "main.py").write_text(
        "import argparse, json, sys\n"
        "from http.server import BaseHTTPRequestHandler, HTTPServer\n"
        f"sys.path.insert(0, {str(PROJECT)!r})\n"
        "from profiles import bootstrap_profile\n"
        "p=argparse.ArgumentParser()\n"
        "p.add_argument('--profile-root')\n"
        "p.add_argument('--profile-child', action='store_true')\n"
        "p.add_argument('--profile-token')\n"
        "args, _=p.parse_known_args()\n"
        "instance=bootstrap_profile(args.profile_root, child=args.profile_child, token=args.profile_token)\n"
        "class Handler(BaseHTTPRequestHandler):\n"
        " def do_GET(self):\n"
        "  self.send_response(200)\n"
        "  self.send_header('X-Pyla-Profile-Token', instance.token)\n"
        "  self.end_headers()\n"
        "  if self.path=='/api/runtime/status':\n"
        "   self.wfile.write(b'{\"runtime\":{\"is_running\":false}}')\n"
        "  else:\n"
        "   self.wfile.write(b'<meta name=\"pyla-ui-token\" content=\"fixture-token\">'+open('cfg/general_config.toml','rb').read())\n"
        " def do_POST(self):\n"
        "  self.send_response(200 if self.headers.get('X-Pyla-UI-Token')=='fixture-token' else 403)\n"
        "  self.send_header('X-Pyla-Profile-Token', instance.token)\n"
        "  self.end_headers()\n"
        "  self.wfile.write(b'{\"runtime\":{\"is_running\":false}}')\n"
        " def log_message(self, *args): pass\n"
        "server=HTTPServer(('127.0.0.1',0), Handler)\n"
        "instance.publish_url('http://127.0.0.1:'+str(server.server_port))\n"
        "server.serve_forever()\n", encoding="utf-8")
    return root


def test_profiles_have_independent_writable_data_and_clear_notifications(installation):
    manager = ProfileManager(installation)
    first = manager.create("Equipe Á")
    second = manager.create("Second")
    a, b = Path(first["path"]), Path(second["path"])
    assert a != b and a.parent == installation / "profiles"
    assert first["slug"] == "equipe-a"
    assert json.loads((a / "latest_brawler_data.json").read_text()) == []
    assert (a / "cfg" / "match_history.csv").read_text().count("\n") == 1
    assert (a / "cfg" / "match_history.csv").read_text().startswith("date_time,")
    webhook = toml.loads((a / "cfg" / "webhook_config.toml").read_text())
    assert webhook["ping_when_stuck"] is True
    assert all(webhook[key] == "" for key in ("webhook_url", "discord_bot_token", "telegram_token", "telegram_chat_id"))
    assert "private-token" in (installation / "cfg" / "webhook_config.toml").read_text()
    assert (a / "cfg" / "login.toml").read_bytes() == (installation / "cfg" / "login.toml").read_bytes()
    for resource in ("cfg/general_config.toml", "models/resource.bin", "playstyles/resource.bin", "api/resource.bin"):
        (a / resource).write_bytes(b"changed only in profile A")
        assert (b / resource).read_bytes() == (installation / resource).read_bytes()
    (a / "latest_brawler_data.json").write_text('[{"brawler":"Colt"}]')
    assert json.loads((b / "latest_brawler_data.json").read_text()) == []
    assert "Shelly" in (installation / "latest_brawler_data.json").read_text()
    assert (a / "LICENSE").read_bytes() == (installation / "LICENSE").read_bytes()
    assert not (a / "profiles").exists()
    assert not (b / "profiles").exists()
    assert len(ProfileManager(installation).list_profiles()) == 2
    assert not list((installation / "profiles").glob("*.tmp"))


def test_immutable_resources_fall_back_to_copy(installation, monkeypatch):
    def unsupported(*args, **kwargs):
        raise OSError("hard links unavailable")
    monkeypatch.setattr(profiles.os, "link", unsupported)
    profile = ProfileManager(installation).create("Copied resources")
    assert (Path(profile["path"]) / "static/resource.bin").read_bytes() == b"original resource"


@pytest.mark.parametrize("name", ["", "..", "../escape", "a\\b", "a\nname", "a:name", "x" * 81, None])
def test_profile_names_reject_paths_and_invalid_input(installation, name):
    with pytest.raises(ValueError):
        ProfileManager(installation).create(name)
    assert not (installation / "profiles").exists()


def test_ids_and_duplicate_names_are_validated(installation):
    manager = ProfileManager(installation)
    manager.create("Work")
    with pytest.raises(ValueError, match="already exists"):
        manager.create("work")
    for profile_id in ("../cfg", "C:\\tmp", "a" * 31, "A" * 32):
        with pytest.raises(ValueError, match="Invalid profile ID"):
            manager.get(profile_id)
        with pytest.raises(ValueError, match="Invalid profile ID"):
            manager.launch(profile_id)


def test_child_cannot_create_nested_profiles(installation):
    created = ProfileManager(installation).create("Child")
    root = Path(created["path"])
    manager = ProfileManager(root)
    assert manager.enabled is False
    assert manager.list_profiles() == []
    with pytest.raises(ValueError, match="main installation"):
        manager.create("Nested")
    assert not (root / "profiles").exists()


@pytest.mark.skipif(os.name == "nt", reason="Windows symlinks require developer mode or administrator access")
def test_symlink_paths_and_recursive_resources_are_rejected(installation, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (installation / "profiles").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symbolic link"):
        ProfileManager(installation).create("Unsafe")
    (installation / "profiles").unlink()
    (installation / "static" / "loop").symlink_to(installation / "static", target_is_directory=True)
    with pytest.raises(ValueError, match="symbolic links"):
        ProfileManager(installation).create("Recursive resource")
    assert ProfileManager(installation).list_profiles() == []


def test_registry_writes_do_not_lose_concurrent_profiles(installation):
    def create(index):
        return ProfileManager(installation).create(f"Profile {index}")
    with ThreadPoolExecutor(max_workers=4) as pool:
        result = list(pool.map(create, range(4)))
    assert len({profile["id"] for profile in result}) == 4
    assert len(ProfileManager(installation).list_profiles()) == 4


class FakeProcess:
    def __init__(self, command, **kwargs):
        self.command, self.kwargs = command, kwargs
        self.pid = 999999999
        self.returncode = None

    def poll(self):
        return self.returncode

    def terminate(self):
        self.returncode = 0

    def wait(self, timeout):
        return self.returncode


def test_frozen_launch_uses_private_runtime_and_argv(installation, monkeypatch):
    internal = installation / "internal"
    (internal / "_internal").mkdir(parents=True)
    executable = internal / "pyla_main.exe"
    executable.write_bytes(b"frozen application")
    (internal / "_internal" / "runtime.dll").write_bytes(b"runtime")
    calls = []
    def popen(command, **kwargs):
        process = FakeProcess(command, **kwargs)
        calls.append(process)
        return process
    manager = ProfileManager(installation, frozen=True, executable=executable, popen_factory=popen)
    created = manager.create("Windows account")
    root = Path(created["path"])
    assert (root / "internal/_internal/runtime.dll").read_bytes() == b"runtime"
    result = manager.launch(created["id"], interface_mode="headless")
    assert result["running"] is True and result["ready"] is False
    assert calls[0].command[0] == str(root / "internal/pyla_main.exe")
    assert "--headless" in calls[0].command
    assert calls[0].kwargs["cwd"] == str(root)
    assert calls[0].kwargs["shell"] is False
    assert calls[0].kwargs["stdin"] == subprocess.DEVNULL
    assert calls[0].kwargs["stderr"] == subprocess.STDOUT
    manager.launch(created["id"])
    assert len(calls) == 1
    monkeypatch.setattr(profiles, "_stop_runtime", lambda *args: None)
    assert manager.stop(created["id"])["running"] is False
    with pytest.raises(ValueError, match="did not launch"):
        ProfileManager(installation).stop(created["id"])


def test_real_source_children_are_isolated_ready_and_not_duplicated(installation):
    manager = ProfileManager(installation)
    first, second = manager.create("First"), manager.create("Second")
    (Path(second["path"]) / "cfg/general_config.toml").write_text('max_fps = "30"\n')
    try:
        a = manager.launch(first["id"], interface_mode="headless", readiness_timeout=8)
        b = manager.launch(second["id"], interface_mode="headless", readiness_timeout=8)
        assert a["running"] and a["ready"]
        assert b["running"] and b["ready"]
        assert a["pid"] != b["pid"] and a["url"] != b["url"]
        opener = build_opener(ProxyHandler({}))
        with opener.open(a["url"], timeout=1) as response:
            assert b'"60"' in response.read()
        with opener.open(b["url"], timeout=1) as response:
            assert b'"30"' in response.read()
        # A fresh parent sees the OS instance lock, even without Popen handles.
        again = ProfileManager(installation).launch(first["id"], interface_mode="headless", readiness_timeout=1)
        assert again["pid"] == a["pid"] and again["ready"]
        assert (Path(a["path"]) / "pyla-profile.log").is_file()
    finally:
        for profile in (first, second):
            if profile["id"] in manager._processes:
                manager.stop(profile["id"])


def test_bootstrap_selects_root_before_app_imports_and_guards_duplicate(installation, monkeypatch):
    created = ProfileManager(installation).create("Bootstrap")
    root = Path(created["path"])
    monkeypatch.chdir(installation)
    instance = bootstrap_profile(root, child=True, token="test-token")
    try:
        assert Path.cwd() == root
        with pytest.raises(ValueError, match="already has a running instance"):
            bootstrap_profile(root, child=True)
        with pytest.raises(ValueError, match="inside this profile"):
            bootstrap_profile(root, frozen=True, executable=installation / "internal/pyla_main.exe")
        instance.publish_url("http://127.0.0.1:5187")
        runtime = json.loads((root / profiles.RUNTIME).read_text())
        assert runtime == {"pid": os.getpid(), "token": "test-token", "url": "http://127.0.0.1:5187"}
        with pytest.raises(ValueError, match="Invalid local profile URL"):
            instance.publish_url("https://example.com")
    finally:
        instance.close()


def test_readiness_requires_the_child_response_header(monkeypatch):
    class Response:
        status = 200
        headers = {"X-Pyla-Profile-Token": "wrong-instance"}
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    class Opener:
        def open(self, *args, **kwargs):
            return Response()
    monkeypatch.setattr(profiles, "build_opener", lambda *args: Opener())
    assert profiles._url_ready("http://127.0.0.1:5185", "expected-instance") is False
    Response.headers["X-Pyla-Profile-Token"] = "expected-instance"
    assert profiles._url_ready("http://127.0.0.1:5185", "expected-instance") is True


def test_stop_leaves_an_active_or_unidentified_child_running(installation, monkeypatch):
    processes = []
    def popen(command, **kwargs):
        process = FakeProcess(command, **kwargs)
        processes.append(process)
        return process
    manager = ProfileManager(installation, popen_factory=popen)
    profile = manager.create("Still playing")
    manager.launch(profile["id"])
    def still_playing(*args):
        raise ValueError("Profile is still stopping; its process has been left running.")
    monkeypatch.setattr(profiles, "_stop_runtime", still_playing)
    with pytest.raises(ValueError, match="left running"):
        manager.stop(profile["id"])
    assert processes[0].poll() is None


def test_source_launcher_preserves_virtualenv_interpreter(installation, tmp_path):
    import sys
    link = tmp_path / "venv-python"
    try:
        link.symlink_to(sys.executable)
    except OSError:
        import pytest
        pytest.skip("Creating symlinks is unavailable")
    manager = ProfileManager(installation, frozen=False, executable=link)
    assert manager.executable == link.absolute()


def test_readiness_uses_launch_identity_when_interpreter_pid_differs(installation, monkeypatch):
    manager = ProfileManager(installation, popen_factory=FakeProcess)
    profile = manager.create("Redirected interpreter")
    manager.launch(profile["id"])
    registry = json.loads(manager.registry.read_text())
    token = registry["profiles"][0]["launch_token"]
    runtime = Path(profile["path"]) / profiles.RUNTIME
    runtime.write_text(json.dumps({"pid":12345,"token":token,"url":"http://127.0.0.1:5187"}))
    monkeypatch.setattr(profiles, "_url_ready", lambda url, supplied: supplied == token)
    result = manager.get(profile["id"])
    assert result["ready"] and result["runtime_pid"] == 12345
    assert result["pid"] != result["runtime_pid"]
    runtime.write_text(json.dumps({"pid":12345,"token":"wrong-launch","url":"http://127.0.0.1:5187"}))
    assert not manager.get(profile["id"])["ready"]
