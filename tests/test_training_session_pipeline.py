from __future__ import annotations

import time
from pathlib import Path

from gui.gui_facade import GuiFacade
from storage.sqlite_store import SqliteStore


def _wait_target(facade: GuiFacade):
    for _ in range(80):
        view = facade.get_game_view()
        targets = [e for e in view.get("entities", []) if e.get("kind") == "target"]
        if targets:
            return targets[0]
        time.sleep(0.01)
    return None


def test_training_session_pipeline(tmp_path):
    db_path = tmp_path / "train.db"
    facade = GuiFacade(mode="live-control", game_id="trace_lock", db_path=str(db_path))

    facade.handle_gui_command("start_training_session", {})
    out = facade.last_command_result
    assert out["status"] == "training_started"
    assert out["session_id"].startswith("training_")
    assert out["session_context"]["session_type"] == "training"

    target = _wait_target(facade)
    assert target is not None
    facade.handle_gui_event("pointer_click", {"x_norm": target["x"], "y_norm": target["y"]})
    assert facade.last_game_event_type == "target_click"
    assert facade.last_platform_index == 0

    facade.handle_gui_event("pointer_click", {"x_norm": 0.0, "y_norm": 0.0})
    assert facade.last_game_event_type == "background_click"
    assert facade.last_platform_index == 1

    before = dict(facade.get_game_hud())
    facade.handle_gui_command("end_training_session", {})
    assert facade.last_command_result["status"] in {"training_completed", "training_stopped"}
    report_path = facade.last_command_result.get("report_path", "")

    facade.handle_gui_event("pointer_click", {"x_norm": 0.5, "y_norm": 0.5})
    after = facade.get_game_hud()
    assert after.get("score") == before.get("score")
    assert after.get("combo") == before.get("combo")

    sid = out["session_id"]
    store = SqliteStore(str(db_path)); store.connect()
    row = store.get_training_session(sid)
    assert row is not None
    assert row["game_id"] == "trace_lock"
    assert row["session_type"] == "training"
    for k in ["accuracy", "omission", "false_action", "rt_stability", "score", "combo", "max_combo", "calibration_status"]:
        assert k in row
    assert "fi_avg" in row and "sqi_avg" in row
    assert report_path and Path(report_path).exists()
    text = Path(report_path).read_text(encoding="utf-8")
    assert "RELIC" in text and "TraceLock Protocol" in text and "Sync Chain" in text and "Trace Drop" in text
    store.close()

    facade2 = GuiFacade(mode="live-control", game_id="trace_lock", db_path=str(db_path))
    facade2.handle_gui_command("start_mock_session", {})
    assert facade2.last_command_result["status"] == "live_debug_started"
    facade2.close()

    facade3 = GuiFacade(mode="live-control", game_id="fake_game", db_path=str(db_path))
    facade3.handle_gui_command("start_mock_session", {})
    assert facade3.last_command_result["status"] == "live_debug_started"
    facade3.close()

    facade.close()
