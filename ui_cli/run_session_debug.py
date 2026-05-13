from __future__ import annotations

import argparse
import json
import time

from runtime.runtime_messages import GameEvent
from session.session_manager import SessionManager
from storage.sqlite_store import SqliteStore


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["demo", "user"], default="demo")
    p.add_argument("--user-id", default="demo_user")
    p.add_argument("--db-path", default="data/relic_local.db")
    p.add_argument("--duration-sec", type=int, default=10)
    p.add_argument("--game-id", default="fake_game")
    p.add_argument("--task6b-config", default="config/task6b.yaml")
    p.add_argument("--list-sessions", action="store_true")
    p.add_argument("--show-session")
    p.add_argument("--show-log-path")
    return p


def main() -> None:
    a = build_parser().parse_args()
    store = SqliteStore(db_path=a.db_path)
    store.connect()
    if a.list_sessions:
        rows = store.list_training_sessions(limit=20)
        for r in rows:
            print(json.dumps({k: r.get(k) for k in ["session_id", "user_id", "game_id", "started_at", "ended_at", "status", "final_fi_avg", "final_sqi_avg", "score"]}, ensure_ascii=False))
        store.close(); return
    if a.show_session:
        row = store.get_training_session(a.show_session)
        if not row: print(f"session not found: {a.show_session}")
        else: print(json.dumps(row, ensure_ascii=False, indent=2))
        store.close(); return
    if a.show_log_path:
        row = store.get_training_session(a.show_log_path)
        if not row: print(f"session not found: {a.show_log_path}")
        else: print(row.get("log_path"))
        store.close(); return

    manager = SessionManager(sqlite_store=store)
    ok, reason, session = manager.start_session(a.user_id, a.game_id, None, task6b_config_path=a.task6b_config, task6b_config_snapshot={"source": "debug"})
    if not ok or not session:
        print(f"start_session failed: {reason}"); store.close(); return
    for i in range(a.duration_sec):
        manager.record_runtime_snapshot({"session_id": session.session_id, "user_id": a.user_id, "game_id": a.game_id, "quality_state": "ok" if i % 3 else "warning", "fi_valid": True, "fi_smoothed": 0.5 + (i % 5) * 0.1, "sqi": 0.8, "control_state": "READY" if i % 4 else "UNRELIABLE_SIGNAL", "behavior_ready": i % 2 == 0, "delta_ms": 1000, "warning_flags": [], "error_flags": []})
        if i == 1:
            manager.record_game_event(GameEvent(event_id="ev1", session_id=session.session_id, game_id=a.game_id, event_type="behavior_sample", created_at_ms=i * 1000, payload={"accuracy": 0.8, "omission": 0.1, "false_action": 0.1, "rt_stability": 0.7}))
        time.sleep(0.01)
    result = manager.end_session(reason="debug_done")
    print(json.dumps({"session_id": session.session_id, "log_path": result.log_path if result else None, "summary": store.get_training_session(session.session_id)}, ensure_ascii=False, indent=2))
    store.close()


if __name__ == "__main__":
    main()
