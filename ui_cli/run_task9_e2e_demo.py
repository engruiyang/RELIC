from __future__ import annotations

import argparse
import json
import subprocess
import sys

from relic_platform.platform_reporter import PlatformReporter
from storage.replay_adapter import ReplayAdapter
from storage.sqlite_store import SqliteStore


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--db-path", default="data/relic_local.db")
    p.add_argument("--duration-sec", type=int, default=5)
    p.add_argument("--user-id", default="demo_user")
    p.add_argument("--game-id", default="fake_game")
    p.add_argument("--task6b-config", default="config/task6b.yaml")
    a = p.parse_args()

    cmd = [sys.executable, "-m", "ui_cli.run_game_debug", "--mode", "demo", "--bridge", "mock", "--duration-sec", str(a.duration_sec), "--user-id", a.user_id, "--db-path", a.db_path, "--game-id", a.game_id, "--task6b-config", a.task6b_config]
    r = subprocess.run(cmd, capture_output=True, text=True, check=True)
    summary = json.loads(r.stdout.strip().splitlines()[-1])

    reporter = PlatformReporter()
    manifest = {"supported_event_types": ["score_update", "behavior_sample", "user_action"]}
    reporter.send(reporter.build_mouse_list(manifest))
    reporter.send(reporter.build_test_start(summary))
    result = reporter.handle_algorithm_stop_test({"type": "ipc_algorithm_stop_test", "session_id": summary["session_id"], "uploaded": True, "error_reason": None})
    reporter.send(reporter.build_test_stop(summary))

    replay = ReplayAdapter()
    replay_stats = replay.replay(summary["log_path"], speed=0)

    store = SqliteStore(db_path=a.db_path)
    store.connect()
    row = store.get_training_session(summary["session_id"]) or {}
    store.close()
    out = {
        "session_id": summary.get("session_id"),
        "user_id": row.get("user_id"),
        "game_id": row.get("game_id"),
        "log_path": summary.get("log_path"),
        "score": row.get("score"),
        "fi_avg": row.get("final_fi_avg"),
        "sqi_avg": row.get("final_sqi_avg"),
        "warning_count": row.get("warning_tick_count"),
        "error_count": row.get("error_count"),
        "platform_report_status": result.status,
        "replay_event_count": replay_stats["event_count"],
    }
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
