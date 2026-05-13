from __future__ import annotations

import json
import subprocess
import sys

from storage.sqlite_store import SqliteStore


def test_run_game_debug_flow(tmp_path) -> None:
    db_path = tmp_path / "task8a.db"
    cmd = [sys.executable, "-m", "ui_cli.run_game_debug", "--mode", "demo", "--duration-sec", "5", "--user-id", "demo_user", "--db-path", str(db_path)]
    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    out = json.loads(p.stdout.strip().splitlines()[-1])
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
    assert out["task6b_config_path"] == "config/task6b.yaml"
    assert "predictor_version" in out


def test_run_game_debug_help_has_task6b_config() -> None:
    p = subprocess.run([sys.executable, "-m", "ui_cli.run_game_debug", "-h"], capture_output=True, text=True, check=True)
    assert "--task6b-config" in p.stdout


def test_run_game_debug_print_jsonl_includes_estimated_fields(tmp_path) -> None:
    db_path = tmp_path / "task8a_print.db"
    cmd = [sys.executable, "-m", "ui_cli.run_game_debug", "--mode", "demo", "--bridge", "mock", "--duration-sec", "2", "--interval", "1", "--user-id", "demo_user", "--db-path", str(db_path), "--print-jsonl"]
    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    lines = [ln for ln in p.stdout.strip().splitlines() if ln.strip()]
    tick_json = json.loads(lines[0])
    inp = tick_json["input"]
    for key in ["attention", "attention_age_ms", "attention_fresh", "gyro_fresh", "sqi", "quality_state", "fi_smoothed", "fi_valid", "control_state", "control_state_reason", "warning_flags", "error_flags"]:
        assert key in inp
    assert inp["fi_valid"] is True
    assert inp["control_state"] in {"STABLE_FOCUS", "HIGH_FOCUS", "DISTRACTED", "UNRELIABLE_SIGNAL"}
    summary = json.loads(lines[-1])
    assert "task6b_config_path" in summary and "predictor_version" in summary
