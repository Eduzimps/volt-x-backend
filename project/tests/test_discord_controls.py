import asyncio
import json
import re
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest


OWNER_ID = 12345
CONTROL_COMMANDS = [
    ("add_to_queue", {"brawler": "shelly"}),
    ("remove_from_queue", {"brawler": "shelly"}),
    ("clear_queue", {}),
    ("activate_playstyle", {"filename": "default_right.pyla"}),
]


@pytest.fixture(autouse=True)
def offline_discord_controls(monkeypatch):
    import requests
    import utils

    def unexpected_network(*args, **kwargs):
        pytest.fail("Discord control tests must not use the network")

    monkeypatch.setattr(requests.sessions.Session, "request", unexpected_network)
    monkeypatch.setattr(utils, "api_base_url", "localhost")


@pytest.fixture
def controls(application):
    service = application.config["data_service"]
    service.update_settings("webhook", {"discord_id": str(OWNER_ID)})
    return application.config["discord_bot"], service


async def invoke_command(bot, name, *, user_id=OWNER_ID, **kwargs):
    interaction = SimpleNamespace(
        user=SimpleNamespace(id=user_id),
        response=SimpleNamespace(send_message=AsyncMock()),
        followup=SimpleNamespace(send=AsyncMock()),
    )
    command = bot.tree.get_command(name)
    assert command is not None, f"/{name} must be a registered slash command"
    await command.callback(interaction, **kwargs)
    interaction.response.send_message.assert_awaited_once()
    assert interaction.response.send_message.await_args.kwargs["ephemeral"] is True
    return interaction.response.send_message.await_args.args[0]


@pytest.mark.parametrize("name,kwargs", CONTROL_COMMANDS)
@pytest.mark.parametrize("authorized_id", [None, OWNER_ID])
def test_control_commands_require_explicit_owner(controls, monkeypatch, name, kwargs, authorized_id):
    bot, service = controls
    monkeypatch.setattr(bot, "get_authorized_user_id", lambda: authorized_id)
    service_spy = Mock(wraps=service)
    monkeypatch.setattr(bot, "data_service", service_spy)

    message = asyncio.run(invoke_command(bot, name, user_id=999, **kwargs))

    assert "disabled" in message if authorized_id is None else "not authorized" in message
    assert service_spy.mock_calls == []
    assert service.get_queue_data() == []


@pytest.mark.parametrize("name", ["start", "stop", "screenshot"])
def test_existing_controls_still_reject_other_users(controls, monkeypatch, name):
    bot, _ = controls
    runtime_spy = Mock()
    window_spy = Mock()
    monkeypatch.setattr(bot, "runtime_manager", runtime_spy)
    monkeypatch.setattr(bot, "window_controller", window_spy)

    assert "not authorized" in asyncio.run(invoke_command(bot, name, user_id=999))
    assert runtime_spy.mock_calls == []
    assert window_spy.mock_calls == []


def test_authorized_queue_crud_persists_and_preserves_progress(controls):
    import utils

    bot, service = controls

    async def scenario():
        assert "Added shelly" in await invoke_command(bot, "add_to_queue", brawler=" SHELLY ")
        assert service.get_queue_data()[0]["push_until"] == 1000
        service.add_or_update_queue_item({
            "brawler": "shelly", "push_until": 1000, "trophies": 432,
            "wins": 7, "win_streak": 3, "automatically_pick": False,
        })
        assert "Updated shelly" in await invoke_command(
            bot, "add_to_queue", brawler="Shelly", target=25, target_type="wins",
        )
        shelly = service.get_queue_data()[0]
        assert (shelly["type"], shelly["push_until"], shelly["trophies"],
                shelly["wins"], shelly["win_streak"], shelly["automatically_pick"]) == (
                    "wins", 25, 432, 7, 3, False,
                )
        assert "Added colt" in await invoke_command(bot, "add_to_queue", brawler="COLT", target=0)
        queue_file = utils.resolve_project_path("latest_brawler_data.json")
        persisted = json.loads(queue_file.read_text())
        assert [item["brawler"] for item in persisted] == ["shelly", "colt"]
        assert persisted[1]["automatically_pick"] is True
        assert "Removed shelly" in await invoke_command(bot, "remove_from_queue", brawler="SHELLY")
        assert [item["brawler"] for item in json.loads(queue_file.read_text())] == ["colt"]
        assert "now empty" in await invoke_command(bot, "clear_queue")
        assert service.get_queue_data() == []
        assert not queue_file.exists() or json.loads(queue_file.read_text()) == []

    asyncio.run(scenario())


@pytest.mark.parametrize("kwargs,expected", [
    ({"brawler": "shelly", "target": -1}, "nonnegative"),
    ({"brawler": "not a brawler"}, "Unknown brawler"),
    ({"brawler": "   "}, "Unknown brawler"),
    ({"brawler": "shelly", "target_type": "invalid"}, "trophies or wins"),
])
def test_invalid_add_does_not_mutate_queue(controls, kwargs, expected):
    bot, service = controls
    assert expected in asyncio.run(invoke_command(bot, "add_to_queue", **kwargs))
    assert service.get_queue_data() == []


@pytest.mark.parametrize("name,kwargs", CONTROL_COMMANDS[:3])
@pytest.mark.parametrize("state", ["running", "paused", "stopping"])
def test_queue_controls_respect_runtime_edit_gate(controls, monkeypatch, name, kwargs, state):
    import utils

    bot, service = controls
    service.add_or_update_queue_item({"brawler": "shelly", "push_until": 1000})
    queue_path = utils.resolve_project_path("latest_brawler_data.json")
    before = queue_path.read_bytes()
    monkeypatch.setattr(bot.runtime_manager, "get_status", lambda: {"state": state, "is_running": True})

    assert "stop the bot first" in asyncio.run(invoke_command(bot, name, **kwargs))
    assert queue_path.read_bytes() == before
    assert len(service.get_queue_data()) == 1


def test_missing_queue_brawler_reports_failure(controls):
    bot, service = controls
    assert "not in the queue" in asyncio.run(invoke_command(bot, "remove_from_queue", brawler="colt"))
    assert service.get_queue_data() == []


def test_authorized_playstyle_activation_persists(controls):
    import utils

    bot, service = controls
    message = asyncio.run(invoke_command(bot, "activate_playstyle", filename=" default_right.pyla "))
    assert "Activated playstyle default_right.pyla" in message
    assert service.get_playstyles_payload()["current"]["filename"] == "default_right.pyla"
    assert utils.load_toml_as_dict("cfg/bot_config.toml", cache=False)["current_playstyle"] == "default_right.pyla"


@pytest.mark.parametrize("filename", ["missing.pyla", "../utils.py", "", "skeleton.py"])
def test_invalid_playstyle_cannot_change_selection(controls, filename):
    bot, service = controls
    before = service.get_playstyles_payload()["current"]
    assert "Failed to activate" in asyncio.run(invoke_command(bot, "activate_playstyle", filename=filename))
    assert service.get_playstyles_payload()["current"] == before


@pytest.mark.parametrize("name,kwargs,method", [
    ("add_to_queue", {"brawler": "shelly"}, "add_or_update_queue_item"),
    ("remove_from_queue", {"brawler": "shelly"}, "delete_queue_item"),
    ("clear_queue", {}, "clear_queue"),
    ("activate_playstyle", {"filename": "default_right.pyla"}, "activate_playstyle"),
])
@pytest.mark.parametrize("error_type", [ValueError, KeyError, OSError])
def test_expected_service_failures_are_ephemeral(controls, monkeypatch, name, kwargs, method, error_type):
    bot, service = controls
    service.add_or_update_queue_item({"brawler": "shelly"})
    monkeypatch.setattr(service, method, Mock(side_effect=error_type("simulated service failure")))

    message = asyncio.run(invoke_command(bot, name, **kwargs))

    assert "Failed" in message
    assert "simulated service failure" in message
    assert [item["brawler"] for item in service.get_queue_data()] == ["shelly"]


def test_help_matches_registered_commands_without_premium_promises(controls):
    bot, _ = controls
    message = asyncio.run(invoke_command(bot, "help"))

    assert set(re.findall(r"`/([^`]+)`", message)) == {command.name for command in bot.tree.get_commands()}
    assert all(name in message for name, _ in CONTROL_COMMANDS)
    assert "Premium" not in message
    assert "push_all" not in message
    assert "switch_player_tag" not in message


def test_add_slash_command_exposes_typed_target_and_choices(controls):
    bot, _ = controls
    parameters = {parameter.name: parameter for parameter in bot.tree.get_command("add_to_queue").parameters}

    assert parameters["brawler"].required is True
    assert parameters["target"].default == 1000
    assert parameters["target_type"].default == "trophies"
    assert {choice.value for choice in parameters["target_type"].choices} == {"trophies", "wins"}
