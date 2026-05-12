import json
from pathlib import Path

from ui_cli.evaluate_task6b import evaluate


def test_evaluate_task6b_basic(tmp_path):
    rows = [
        {"now_ms": 1000, "attention": 65, "attention_seen_once": True, "attention_age_ms": 200, "attention_fresh": True, "gyro_x": 0.1, "gyro_y": 0.1, "gyro_z": 0.1, "gyro_seen_once": True, "gyro_age_ms": 100, "gyro_fresh": True, "device_connected": True, "stream_alive": True, "warning_flags": [], "error_flags": []}
    ]
    labels = [{"start_ms": 0, "end_ms": 2000, "label": "STABLE_FOCUS"}]
    out = evaluate(rows, labels, {"fi_ema_alpha": 0.7})
    assert "macro_f1" in out
    assert "confusion_matrix" in out


def test_tune_task6b_runs(tmp_path):
    log = tmp_path / "a.jsonl"
    label = tmp_path / "a.yaml"
    cfg = tmp_path / "cfg.yaml"
    out = tmp_path / "out.json"
    log.write_text(json.dumps({"now_ms": 1000, "attention": 65, "attention_seen_once": True, "attention_age_ms": 200, "attention_fresh": True, "gyro_x": 0.1, "gyro_y": 0.1, "gyro_z": 0.1, "gyro_seen_once": True, "gyro_age_ms": 100, "gyro_fresh": True, "device_connected": True, "stream_alive": True, "warning_flags": [], "error_flags": []}) + "\n", encoding="utf-8")
    label.write_text(json.dumps({"segments": [{"start_ms": 0, "end_ms": 2000, "label": "STABLE_FOCUS"}]}), encoding="utf-8")
    cfg.write_text(json.dumps({"fi_ema_alpha": 0.7}), encoding="utf-8")
    import subprocess, sys
    r = subprocess.run([sys.executable, "-m", "ui_cli.tune_task6b", "--input", str(log), "--labels", str(label), "--base-config", str(cfg), "--trials", "50", "--method", "random", "--out", str(out)], check=True)
    assert out.exists()
