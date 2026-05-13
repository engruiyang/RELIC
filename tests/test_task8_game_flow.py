from __future__ import annotations

import json
import subprocess
import sys

from storage.sqlite_store import SqliteStore


def test_run_game_debug_flow(tmp_path) -> None:
    db_path = tmp_path / "task8a.db"
    cmd = [sys.executable, "-m", "ui_cli.run_game_debug", "--mode", "demo", "--duration-sec", "5", "--user-id", "demo_user", "--db-path", str(db_path)]
    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    out = json.loads(p.stdout)
    assert out["game_event_count"] > 0
    assert out["behavior_sample_count"] > 0
    assert out["log_path"].startswith("logs/sessions/")
    assert "logs/task6b" not in out["log_path"]

    store = SqliteStore(db_path=str(db_path)); store.connect()
    row = store.get_training_session(out["session_id"])
    store.close()
    assert row is not None
    assert row["game_event_count"] > 0
    assert row["behavior_sample_count"] > 0
