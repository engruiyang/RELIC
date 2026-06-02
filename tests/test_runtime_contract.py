import json

import pytest

from runtime.local_runtime import LocalRuntime
from runtime.runtime_messages import GameEvent, RuntimeCommand, RuntimeContractError, RuntimeSnapshotView


def test_snapshot_from_dict_and_json() -> None:
    snapshot = RuntimeSnapshotView.from_dict({"session_id": "s1", "attention": 0.9})
    payload = snapshot.to_dict()
    assert payload["session_id"] == "s1"
    json.dumps(payload)


def test_runtime_command_to_json() -> None:
    command = RuntimeCommand(
        command_id="c1",
        session_id="s1",
        game_id="g1",
        command_type="start_game",
        issued_at_ms=100,
        payload={"difficulty": 2},
    )
    json.dumps(command.to_dict())


def test_game_event_behavior_sample_to_json_and_clip() -> None:
    event = GameEvent(
        event_id="e1",
        session_id="s1",
        game_id="g1",
        event_type="behavior_sample",
        created_at_ms=100,
        payload={"accuracy": 1.5, "omission": -0.2, "false_action": 0.6, "rt_stability": 3.0},
    )
    payload = event.to_dict()["payload"]
    assert payload["accuracy"] == 1.0
    assert payload["omission"] == 0.0
    assert payload["false_action"] == 0.6
    assert payload["rt_stability"] == 1.0
    json.dumps(event.to_dict())


def test_local_runtime_publish_snapshot() -> None:
    runtime = LocalRuntime()
    received: list[RuntimeSnapshotView] = []
    runtime.subscribe_snapshots(received.append)
    snapshot = RuntimeSnapshotView(session_id="s1")
    runtime.publish_snapshot(snapshot)
    assert received and received[0].session_id == "s1"


def test_local_runtime_emit_game_event() -> None:
    runtime = LocalRuntime()
    received: list[GameEvent] = []
    runtime.subscribe_game_events(received.append)
    event = GameEvent(
        event_id="e1",
        session_id="s1",
        game_id="g1",
        event_type="score_update",
        created_at_ms=1,
        payload={"score": 10},
    )
    runtime.emit_game_event(event)
    assert received and received[0].event_id == "e1"


def test_game_event_requires_session_id_and_game_id() -> None:
    with pytest.raises(RuntimeContractError):
        GameEvent(event_id="e", session_id="", game_id="g1", event_type="score_update", created_at_ms=1)
    with pytest.raises(RuntimeContractError):
        GameEvent(event_id="e", session_id="s1", game_id="", event_type="score_update", created_at_ms=1)


def test_runtime_message_rejects_non_json_serializable() -> None:
    with pytest.raises(RuntimeContractError):
        GameEvent(
            event_id="e1",
            session_id="s1",
            game_id="g1",
            event_type="score_update",
            created_at_ms=1,
            payload={"bad": object()},
        )


def test_runtime_module_no_pygame_or_sqlite_dependency() -> None:
    for module_path in ["runtime/runtime_api.py", "runtime/runtime_messages.py", "runtime/local_runtime.py"]:
        content = open(module_path, "r", encoding="utf-8").read().lower()
        assert "pygame" not in content
        assert "sqlite" not in content
