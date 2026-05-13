from __future__ import annotations

from game.fake_game_client import FakeGameClient
from game.game_manager import GameManager
from game.game_manifest import GameManifest
from game.renderer_adapter import HeadlessRendererStub, input_to_runtime_command, input_to_user_action_event
from runtime.local_runtime import LocalRuntime
from runtime.runtime_messages import RuntimeSnapshotView


def _manifest() -> GameManifest:
    return GameManifest(game_id="fake_game", display_name="Fake", version="0.1", supported_event_types=["score_update", "behavior_sample", "difficulty_request", "game_completed", "game_error", "user_action"], supported_command_types=["start_game", "pause_game", "resume_game", "stop_game"], description="test")


def test_headless_renderer_stub_receives_view_state() -> None:
    rt = LocalRuntime(); gm = GameManager(rt)
    renderer = HeadlessRendererStub()
    gm.register_renderer(renderer)
    gm.register_game(_manifest(), FakeGameClient())
    gm.select_game("fake_game")
    gm.start_game("s1")
    rt.publish_snapshot(RuntimeSnapshotView(session_id="s1", game_id="fake_game", fi_valid=True, fi_smoothed=0.7, sqi=0.9, control_state="STABLE_FOCUS", quality_state="ok", now_ms=1000))
    assert renderer.last_view_state is not None
    assert renderer.last_view_state["schema_version"] == "game_view.v1"


def test_input_conversion_to_runtime_command_and_user_action() -> None:
    cmd = input_to_runtime_command(command_id="c1", session_id="s1", game_id="fake_game", action="pause_game", issued_at_ms=100)
    assert cmd.command_type == "pause_game"
    ev = input_to_user_action_event(event_id="e1", session_id="s1", game_id="fake_game", created_at_ms=120, action_type="click", target_id="target_1", success=True, rt_ms=430)
    assert ev.event_type == "user_action"
    assert ev.payload["action_type"] == "click"
