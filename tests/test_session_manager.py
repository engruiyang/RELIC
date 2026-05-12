import json
from pathlib import Path

from runtime.runtime_messages import GameEvent
from session.session_manager import SessionManager
from storage.sqlite_store import SqliteStore


def _build_manager(tmp_path):
    db = tmp_path / "test.db"
    store = SqliteStore(str(db))
    store.connect()
    mgr = SessionManager(store, logs_dir=str(tmp_path / "logs" / "sessions"), default_tick_ms=100)
    return mgr, store


def test_start_session_creates_active_session(tmp_path):
    mgr, store = _build_manager(tmp_path)
    ok, _, s = mgr.start_session("u1", "g1", "c1")
    assert ok and s is not None and mgr.has_active_session()
    store.close()


def test_start_session_creates_jsonl_log(tmp_path):
    mgr, store = _build_manager(tmp_path)
    ok, _, s = mgr.start_session("u1", "g1", "c1")
    assert ok and Path(s.log_path).exists()
    store.close()


def test_record_runtime_snapshot_writes_jsonl(tmp_path):
    mgr, store = _build_manager(tmp_path)
    ok, _, s = mgr.start_session("u1", "g1", "c1")
    mgr.record_runtime_snapshot({"quality_state": "ok", "fi_valid": True, "fi_smoothed": 0.5, "sqi": 0.7, "delta_ms": 100})
    mgr.end_session()
    lines = Path(s.log_path).read_text(encoding="utf-8").strip().splitlines()
    assert any(json.loads(x)["event_type"] == "runtime_snapshot" for x in lines)
    store.close()


def test_record_game_event_writes_jsonl(tmp_path):
    mgr, store = _build_manager(tmp_path)
    ok, _, s = mgr.start_session("u1", "g1", "c1")
    mgr.record_game_event(GameEvent(event_id="e1", session_id=s.session_id, game_id="g1", event_type="score_update", created_at_ms=1, payload={"score": 1}))
    mgr.end_session()
    lines = Path(s.log_path).read_text(encoding="utf-8").strip().splitlines()
    assert any(json.loads(x)["event_type"] == "game_event" for x in lines)
    store.close()


def test_mismatched_game_event_session_is_rejected(tmp_path):
    mgr, store = _build_manager(tmp_path)
    ok, _, s = mgr.start_session("u1", "g1", "c1")
    assert not mgr.record_game_event(GameEvent(event_id="e1", session_id="bad", game_id="g1", event_type="score_update", created_at_ms=1, payload={}))
    mgr.end_session()
    store.close()


def test_end_session_writes_sqlite_summary(tmp_path):
    mgr, store = _build_manager(tmp_path)
    ok, _, s = mgr.start_session("u1", "g1", "c1")
    mgr.record_runtime_snapshot({"quality_state": "ok", "fi_valid": True, "fi_smoothed": 0.5, "sqi": 0.7})
    mgr.end_session()
    row = store.get_training_session(s.session_id)
    assert row is not None and row["status"] == "ended"
    store.close()


def test_warning_duration_is_accumulated(tmp_path):
    mgr, store = _build_manager(tmp_path)
    ok, _, _ = mgr.start_session("u1", "g1", "c1")
    mgr.record_runtime_snapshot({"quality_state": "warning", "delta_ms": 100})
    s = mgr.end_session()
    assert s.warning_duration_ms == 100
    store.close()


def test_unreliable_duration_is_accumulated(tmp_path):
    mgr, store = _build_manager(tmp_path)
    ok, _, _ = mgr.start_session("u1", "g1", "c1")
    mgr.record_runtime_snapshot({"quality_state": "invalid", "delta_ms": 100})
    s = mgr.end_session()
    assert s.unreliable_duration_ms == 100
    store.close()


def test_control_state_summary_is_counted(tmp_path):
    mgr, store = _build_manager(tmp_path)
    ok, _, _ = mgr.start_session("u1", "g1", "c1")
    mgr.record_runtime_snapshot({"control_state": "READY"})
    s = mgr.end_session()
    assert s.control_state_summary["READY"] == 1
    store.close()


def test_behavior_ready_ratio_is_counted(tmp_path):
    mgr, store = _build_manager(tmp_path)
    ok, _, _ = mgr.start_session("u1", "g1", "c1")
    mgr.record_runtime_snapshot({"behavior_ready": True})
    mgr.record_runtime_snapshot({"behavior_ready": False})
    s = mgr.end_session()
    assert s.behavior_ready_ratio == 0.5
    store.close()


def test_has_behavior_samples_is_set_after_behavior_event(tmp_path):
    mgr, store = _build_manager(tmp_path)
    ok, _, s0 = mgr.start_session("u1", "g1", "c1")
    mgr.record_game_event(GameEvent(event_id="e1", session_id=s0.session_id, game_id="g1", event_type="behavior_sample", created_at_ms=1, payload={"accuracy": 0.5, "omission": 0.2, "false_action": 0.1, "rt_stability": 0.6}))
    s = mgr.end_session()
    assert s.has_behavior_samples is True
    store.close()


def test_cannot_start_two_sessions(tmp_path):
    mgr, store = _build_manager(tmp_path)
    ok, _, _ = mgr.start_session("u1", "g1", "c1")
    ok2, reason, _ = mgr.start_session("u1", "g1", "c1")
    assert ok and (not ok2) and reason == "active_session_exists"
    store.close()


def test_abort_session_writes_aborted_summary(tmp_path):
    mgr, store = _build_manager(tmp_path)
    ok, _, s = mgr.start_session("u1", "g1", "c1")
    mgr.abort_session("x")
    row = store.get_training_session(s.session_id)
    assert row["status"] == "aborted"
    store.close()


def test_logs_sessions_path_is_used_not_logs_task6b(tmp_path):
    mgr, store = _build_manager(tmp_path)
    ok, _, s = mgr.start_session("u1", "g1", "c1")
    assert "logs/sessions" in s.log_path
    assert "logs/task6b" not in s.log_path
    mgr.end_session()
    store.close()
