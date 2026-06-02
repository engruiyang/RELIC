from __future__ import annotations

import json
import subprocess
import sys

from game.fake_game_client import FakeGameClient
from game.game_manager import GameManager
from game.game_manifest import GameManifest
from game.game_pipeline import GamePipelineRunner
from runtime.local_runtime import LocalRuntime
from session.session_manager import SessionManager
from storage.sqlite_store import SqliteStore


def _manifest() -> GameManifest:
    return GameManifest(game_id="fake_game", display_name="Fake", version="0.1", supported_event_types=["score_update", "behavior_sample", "difficulty_request", "game_completed", "game_error", "user_action"], supported_command_types=["start_game", "pause_game", "resume_game", "stop_game"], description="test")


def test_pipeline_runner_process_snapshot_and_jsonl(tmp_path) -> None:
    db = tmp_path / "p.db"
    pipeline_log = tmp_path / "logs" / "game_debug" / "p.pipeline.jsonl"
    store = SqliteStore(db_path=str(db)); store.connect()
    sm = SessionManager(sqlite_store=store)
    ok, _, sess = sm.start_session("demo_user", "fake_game", None)
    assert ok and sess is not None
    rt = LocalRuntime(); gm = GameManager(rt, sm)
    gm.register_game(_manifest(), FakeGameClient()); gm.select_game("fake_game"); gm.start_game(sess.session_id)
    runner = GamePipelineRunner(runtime=rt, game_manager=gm, session_manager=sm, session_id=sess.session_id, user_id="demo_user", game_id="fake_game", pipeline_jsonl_path=str(pipeline_log))
    r1 = runner.process_snapshot({"now_ms": 1000, "attention": 65, "attention_fresh": True, "gyro_fresh": True, "sqi": 0.9, "quality_state": "ok", "fi_smoothed": 0.7, "fi_valid": True, "control_state": "STABLE_FOCUS", "control_state_reason": "x", "warning_flags": [], "error_flags": [], "delta_ms": 1000, "behavior_ready": True})
    assert r1.output["event_count"] >= 2
    r2 = runner.process_snapshot({"now_ms": 2000, "attention": 40, "attention_fresh": True, "gyro_fresh": True, "sqi": 0.5, "quality_state": "warning", "fi_smoothed": 0.2, "fi_valid": True, "control_state": "UNRELIABLE_SIGNAL", "control_state_reason": "x", "warning_flags": [], "error_flags": [], "delta_ms": 1000, "behavior_ready": True})
    assert "behavior_sample" not in r2.output["event_types"]
    json.dumps(r1.to_dict())
    runner.stop(); runner.close()
    sm.end_session("done")
    row = store.get_training_session(sess.session_id)
    store.close()
    assert row is not None and row["game_event_count"] > 0 and row["behavior_sample_count"] > 0
    assert pipeline_log.exists()
    assert "logs/task6b" not in str(pipeline_log)


def test_run_game_debug_mock_and_live_argparse(tmp_path) -> None:
    db = tmp_path / "cli.db"
    cmd = [sys.executable, "-m", "ui_cli.run_game_debug", "--bridge", "mock", "--mode", "demo", "--duration-sec", "2", "--user-id", "demo_user", "--db-path", str(db), "--game-id", "fake_game", "--print-jsonl"]
    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    lines = [x for x in p.stdout.splitlines() if x.strip()]
    final = json.loads(lines[-1])
    assert final["game_event_count"] > 0
    assert final["behavior_sample_count"] > 0
    assert final["view_state"]["schema_version"] == "game_view.v1"
