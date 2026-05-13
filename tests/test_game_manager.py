from __future__ import annotations

from game.fake_game_client import FakeGameClient
from game.game_manager import GameManager
from game.game_manifest import GameManifest
from runtime.local_runtime import LocalRuntime
from runtime.runtime_messages import RuntimeSnapshotView


class StubSession:
    def __init__(self):
        self.events = []
    def has_active_session(self):
        return True
    def record_game_event(self, e):
        self.events.append(e)


def _manifest() -> GameManifest:
    return GameManifest(game_id="fake_game", display_name="Fake", version="0.1", supported_event_types=["score_update", "behavior_sample", "difficulty_request", "game_completed", "game_error", "user_action"], supported_command_types=["start_game", "pause_game", "resume_game", "stop_game"], description="test")


def test_register_list_select_start_stop() -> None:
    rt = LocalRuntime(); ss = StubSession(); gm = GameManager(rt, ss)
    gm.register_game(_manifest(), FakeGameClient())
    assert gm.select_game("fake_game") is True
    assert any(x["game_id"] == "fake_game" for x in gm.list_games())
    assert gm.start_game("s1") is True
    rt.publish_snapshot(RuntimeSnapshotView(session_id="s1", game_id="fake_game", fi_valid=True, fi_smoothed=0.8, control_state="STABLE_FOCUS", quality_state="ok", now_ms=1000))
    assert len(ss.events) > 0
    assert gm.stop_game(issued_at_ms=2000) is True


def test_mismatched_session_event_rejected() -> None:
    rt = LocalRuntime(); ss = StubSession(); gm = GameManager(rt, ss)
    gm.register_game(_manifest(), FakeGameClient())
    gm.select_game("fake_game"); gm.start_game("s1")
    rt.publish_snapshot(RuntimeSnapshotView(session_id="other", game_id="fake_game", fi_valid=True, fi_smoothed=0.8, control_state="STABLE_FOCUS", quality_state="ok", now_ms=1000))
    assert ss.events == []
