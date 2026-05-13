import json
from pathlib import Path
import subprocess
import sys

from runtime.runtime_messages import GameEvent
from session.session_manager import SessionManager
from storage.sqlite_store import SqliteStore


def _build_manager(tmp_path):
    db = tmp_path / "test.db"
    store = SqliteStore(str(db)); store.connect()
    return SessionManager(store, logs_dir=str(tmp_path / "logs" / "sessions"), default_tick_ms=100), store


def test_log_path_is_cross_platform_and_not_task6b(tmp_path):
    mgr, store = _build_manager(tmp_path)
    ok, _, s = mgr.start_session("u1", "g1", "c1")
    parts = Path(s.log_path).parts
    assert "logs" in parts and "sessions" in parts and "task6b" not in parts
    mgr.end_session(); store.close()


def test_training_session_summary_contains_duration_summaries(tmp_path):
    mgr, store = _build_manager(tmp_path)
    ok, _, s = mgr.start_session("u1", "g1", "c1")
    mgr.record_runtime_snapshot({"quality_state": "ok", "control_state": "READY", "delta_ms": 100})
    mgr.end_session(); row = store.get_training_session(s.session_id)
    assert row["quality_state_duration_summary"] and row["control_state_duration_summary"]


def test_quality_state_duration_summary_is_counted(tmp_path):
    mgr, store = _build_manager(tmp_path); ok, _, s = mgr.start_session("u1", "g1", "c1")
    mgr.record_runtime_snapshot({"quality_state": "warning", "delta_ms": 120}); mgr.end_session(); row = store.get_training_session(s.session_id)
    assert json.loads(row["quality_state_duration_summary"])["warning"] == 120


def test_control_state_duration_summary_is_counted(tmp_path):
    mgr, store = _build_manager(tmp_path); ok, _, s = mgr.start_session("u1", "g1", "c1")
    mgr.record_runtime_snapshot({"control_state": "UNRELIABLE_SIGNAL", "delta_ms": 130}); mgr.end_session(); row = store.get_training_session(s.session_id)
    assert json.loads(row["control_state_duration_summary"])["UNRELIABLE_SIGNAL"] == 130


def test_fi_min_max_last_are_counted(tmp_path):
    mgr, store = _build_manager(tmp_path); ok, _, s = mgr.start_session("u1", "g1", "c1")
    mgr.record_runtime_snapshot({"fi_smoothed": 0.2}); mgr.record_runtime_snapshot({"fi_smoothed": 0.9}); mgr.end_session(); row = store.get_training_session(s.session_id)
    assert row["fi_min"] == 0.2 and row["fi_max"] == 0.9 and row["fi_last"] == 0.9


def test_sqi_min_max_last_are_counted(tmp_path):
    mgr, store = _build_manager(tmp_path); ok, _, s = mgr.start_session("u1", "g1", "c1")
    mgr.record_runtime_snapshot({"sqi": 0.3}); mgr.record_runtime_snapshot({"sqi": 0.7}); mgr.end_session(); row = store.get_training_session(s.session_id)
    assert row["sqi_min"] == 0.3 and row["sqi_max"] == 0.7 and row["sqi_last"] == 0.7


def test_score_update_updates_score_summary(tmp_path):
    mgr, store = _build_manager(tmp_path); ok, _, s = mgr.start_session("u1", "g1", "c1")
    mgr.record_game_event(GameEvent(event_id="e1", session_id=s.session_id, game_id="g1", event_type="score_update", created_at_ms=1, payload={"score": 10, "score_delta": 2}))
    mgr.end_session(); row = store.get_training_session(s.session_id)
    assert row["score_last"] == 10 and row["score_total_delta"] == 2 and row["score_update_count"] == 1


def test_behavior_sample_count_sets_has_behavior_samples(tmp_path):
    mgr, store = _build_manager(tmp_path); ok, _, s = mgr.start_session("u1", "g1", "c1")
    mgr.record_game_event(GameEvent(event_id="e1", session_id=s.session_id, game_id="g1", event_type="behavior_sample", created_at_ms=1, payload={"accuracy": 0.5, "omission": 0.2, "false_action": 0.1, "rt_stability": 0.6}))
    mgr.end_session(); row = store.get_training_session(s.session_id)
    assert row["has_behavior_samples"] == 1 and row["behavior_sample_count"] == 1


def test_game_completed_updates_completion_summary(tmp_path):
    mgr, store = _build_manager(tmp_path); ok, _, s = mgr.start_session("u1", "g1", "c1")
    mgr.record_game_event(GameEvent(event_id="e1", session_id=s.session_id, game_id="g1", event_type="game_completed", created_at_ms=1, payload={"reason": "done", "final_score": 99, "user_finished": True}))
    mgr.end_session(); row = store.get_training_session(s.session_id)
    assert row["game_completed"] == 1 and row["game_completion_reason"] == "done" and row["score_last"] == 99


def test_mismatched_game_event_is_rejected_and_warning_logged(tmp_path):
    mgr, store = _build_manager(tmp_path); ok, _, s = mgr.start_session("u1", "g1", "c1")
    assert not mgr.record_game_event(GameEvent(event_id="e1", session_id="bad", game_id="g1", event_type="score_update", created_at_ms=1, payload={}))
    mgr.end_session(); lines = Path(tmp_path / "logs" / "sessions" / f"{s.session_id}.jsonl").read_text(encoding="utf-8").splitlines()
    assert any(json.loads(x)["event_type"] == "warning" for x in lines)


def test_session_summary_event_written_before_session_end(tmp_path):
    mgr, store = _build_manager(tmp_path); ok, _, s = mgr.start_session("u1", "g1", "c1")
    mgr.end_session(); events = [json.loads(x)["event_type"] for x in Path(tmp_path / "logs" / "sessions" / f"{s.session_id}.jsonl").read_text(encoding="utf-8").splitlines()]
    assert events.index("session_summary") < events.index("session_end")


def test_list_sessions_cli_outputs_recent_sessions(tmp_path):
    db = tmp_path / "cli.db"
    subprocess.run([sys.executable, "-m", "ui_cli.run_session_debug", "--mode", "demo", "--duration-sec", "1", "--db-path", str(db)], check=True, capture_output=True, text=True)
    res = subprocess.run([sys.executable, "-m", "ui_cli.run_session_debug", "--list-sessions", "--db-path", str(db)], check=True, capture_output=True, text=True)
    assert "session_id" in res.stdout and "final_fi_avg" in res.stdout


def test_show_session_cli_outputs_summary(tmp_path):
    db = tmp_path / "cli.db"
    run = subprocess.run([sys.executable, "-m", "ui_cli.run_session_debug", "--mode", "demo", "--duration-sec", "1", "--db-path", str(db)], check=True, capture_output=True, text=True)
    sid = json.loads(run.stdout)["session_id"]
    res = subprocess.run([sys.executable, "-m", "ui_cli.run_session_debug", "--show-session", sid, "--db-path", str(db)], check=True, capture_output=True, text=True)
    assert sid in res.stdout and "status" in res.stdout
