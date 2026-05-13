from __future__ import annotations

import json

from game.fake_game_client import FakeGameClient
from runtime.runtime_messages import RuntimeCommand, RuntimeSnapshotView


def _start(client: FakeGameClient, sid: str = "s1"):
    client.on_command(RuntimeCommand(command_id="c1", session_id=sid, game_id="fake_game", command_type="start_game", issued_at_ms=0, payload={}))


def test_emit_score_and_behavior_on_stable_snapshot() -> None:
    c = FakeGameClient()
    _start(c)
    events = c.on_snapshot(RuntimeSnapshotView(session_id="s1", game_id="fake_game", fi_valid=True, fi_smoothed=0.8, control_state="STABLE_FOCUS", quality_state="ok", now_ms=1000))
    kinds = {e.event_type for e in events}
    assert "score_update" in kinds
    assert "behavior_sample" in kinds


def test_no_behavior_sample_when_unreliable() -> None:
    c = FakeGameClient()
    _start(c)
    events = c.on_snapshot(RuntimeSnapshotView(session_id="s1", game_id="fake_game", fi_valid=True, fi_smoothed=0.4, control_state="UNRELIABLE_SIGNAL", quality_state="warning", now_ms=1000))
    assert all(e.event_type != "behavior_sample" for e in events)


def test_view_state_json_serializable() -> None:
    c = FakeGameClient()
    _start(c)
    c.on_snapshot(RuntimeSnapshotView(session_id="s1", game_id="fake_game", fi_valid=True, fi_smoothed=0.6, sqi=0.9, control_state="HIGH_FOCUS", quality_state="ok", now_ms=1000))
    json.dumps(c.get_view_state().to_dict())
