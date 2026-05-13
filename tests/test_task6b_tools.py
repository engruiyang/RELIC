import json
from pathlib import Path

from ui_cli.evaluate_task6b import evaluate


def test_evaluate_task6b_basic(tmp_path):
    rows = [
        {"now_ms": 1000, "attention": 65, "attention_seen_once": True, "attention_age_ms": 200, "attention_fresh": True, "gyro_x": 0.1, "gyro_y": 0.1, "gyro_z": 0.1, "gyro_seen_once": True, "gyro_age_ms": 100, "gyro_fresh": True, "device_connected": True, "stream_alive": True, "warning_flags": [], "error_flags": []}
    ]
    labels = [{"start_ms": 0, "end_ms": 2000, "label": "STABLE_FOCUS"}]
    out = evaluate(rows, labels, {"fi_ema_alpha": 0.7})
    assert "overall" in out
    assert "macro_f1" in out["overall"]


def test_evaluate_sec_label_and_session_match(tmp_path):
    rows = [
        {"session_id": "A", "now_ms": 1000, "attention": 65, "attention_seen_once": True, "attention_age_ms": 200, "attention_fresh": True, "gyro_x": 0.1, "gyro_y": 0.1, "gyro_z": 0.1, "gyro_seen_once": True, "gyro_age_ms": 100, "gyro_fresh": True, "device_connected": True, "stream_alive": True, "warning_flags": [], "error_flags": []},
        {"session_id": "B", "now_ms": 1000, "attention": 10, "attention_seen_once": True, "attention_age_ms": 200, "attention_fresh": True, "gyro_x": 0.1, "gyro_y": 0.1, "gyro_z": 0.1, "gyro_seen_once": True, "gyro_age_ms": 100, "gyro_fresh": True, "device_connected": True, "stream_alive": True, "warning_flags": [], "error_flags": []},
    ]
    labels = [{"start": 0, "end": 2, "label": "STABLE_FOCUS"}]
    out = evaluate([r for r in rows if r["session_id"] == "A"], labels, {"fi_ema_alpha": 0.7}, label_meta={"time_unit": "sec", "session_id": "A"})
    assert out["overall"]["frame_accuracy"] >= 0.0


def test_evaluate_ignore_frame():
    rows = [{"session_id": "A", "now_ms": 1000, "attention": 65, "attention_seen_once": True, "attention_age_ms": 200, "attention_fresh": True, "gyro_x": 0.1, "gyro_y": 0.1, "gyro_z": 0.1, "gyro_seen_once": True, "gyro_age_ms": 100, "gyro_fresh": True, "device_connected": True, "stream_alive": True, "warning_flags": [], "error_flags": []}]
    labels = [{"session_id": "A", "start_ms": 0, "end_ms": 3000, "label": "IGNORE"}]
    out = evaluate(rows, labels, {"fi_ema_alpha": 0.7}, label_meta={"mode": "frames"})
    assert out["overall"]["total_labeled_frames"] == 0


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
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["top_candidates"]
    assert all(c["validation"] for c in payload["top_candidates"])
    for c in payload["top_candidates"]:
        cfgv = c["config"]
        assert cfgv["imu_rate_soft_mult"] < cfgv["imu_rate_bad_mult"]
        assert cfgv["imu_jitter_soft_mult"] < cfgv["imu_jitter_bad_mult"]
        assert cfgv["stable_exit"] <= cfgv["stable_enter"]
        assert cfgv["distracted_enter"] < cfgv["stable_enter"]
        assert cfgv["attention_low_fallback"] + 20 <= cfgv["attention_high_fallback"]


def test_record_generates_label_template(tmp_path):
    import subprocess, sys
    out_log = tmp_path / "x.jsonl"
    out_lbl = tmp_path / "x.frames.csv"
    subprocess.run([sys.executable, "-m", "ui_cli.run_core_debug", "--bridge", "mock", "--mode", "demo", "--duration-sec", "1", "--session-id", "task6b_mock_demo_smoke_20260512_000000", "--record-jsonl", str(out_log), "--frame-label-template", str(out_lbl), "--frame-sec", "3"], check=True)
    assert out_log.exists()
    assert out_lbl.exists()


def test_evaluate_task6b_smoke_output_file(tmp_path):
    log = tmp_path / "s.jsonl"
    lbl = tmp_path / "s.frames.csv"
    cfg = tmp_path / "cfg.yaml"
    out = tmp_path / "report.json"
    log.write_text(json.dumps({"session_id": "S", "now_ms": 1000, "attention": 65, "attention_seen_once": True, "attention_age_ms": 200, "attention_fresh": True, "gyro_x": 0.1, "gyro_y": 0.1, "gyro_z": 0.1, "gyro_seen_once": True, "gyro_age_ms": 100, "gyro_fresh": True, "device_connected": True, "stream_alive": True, "q_motion": None, "warning_flags": [], "error_flags": []}) + "\n", encoding="utf-8")
    lbl.write_text("session_id,frame_id,start_ms,end_ms,start_sec,end_sec,label,confidence,note\nS,0,0,3000,0,3,STABLE_FOCUS,low,\n", encoding="utf-8")
    cfg.write_text("fi_ema_alpha: 0.7\n", encoding="utf-8")
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "ui_cli.evaluate_task6b", "--input", str(log), "--labels", str(lbl), "--config", str(cfg), "--out", str(out)], check=True)
    assert out.exists()


def test_evaluate_multi_session_and_unreliable_miss(tmp_path):
    rows = [
        {"session_id": "A", "now_ms": 1000, "attention": 65, "attention_seen_once": True, "attention_age_ms": 100, "attention_fresh": True, "gyro_x": 0.0, "gyro_y": 0.0, "gyro_z": 0.0, "gyro_seen_once": True, "gyro_age_ms": 100, "gyro_fresh": True, "device_connected": True, "stream_alive": True, "warning_flags": [], "error_flags": []},
        {"session_id": "B", "now_ms": 1000, "attention": 65, "attention_seen_once": True, "attention_age_ms": 100, "attention_fresh": True, "gyro_x": 0.0, "gyro_y": 0.0, "gyro_z": 0.0, "gyro_seen_once": True, "gyro_age_ms": 100, "gyro_fresh": True, "device_connected": True, "stream_alive": True, "warning_flags": [], "error_flags": []},
    ]
    labels = [
        {"session_id": "A", "start_ms": 0, "end_ms": 2000, "label": "STABLE_FOCUS"},
        {"session_id": "B", "start_ms": 0, "end_ms": 2000, "label": "UNRELIABLE_SIGNAL"},
    ]
    payload = evaluate(rows, labels, {"fi_ema_alpha": 0.7}, label_meta={"mode": "frames"})
    assert {x["session_id"] for x in payload["per_session"]} == {"A", "B"}
    assert payload["overall"]["total_labeled_frames"] == 2
    assert payload["overall"]["unreliable_miss"] > 0


def test_tune_task6b_multi_session_report_meta(tmp_path):
    import subprocess, sys
    (tmp_path / "a.jsonl").write_text(json.dumps({"session_id": "A", "now_ms": 1000, "attention": 65, "attention_seen_once": True, "attention_age_ms": 100, "attention_fresh": True, "gyro_x": 0.0, "gyro_y": 0.0, "gyro_z": 0.0, "gyro_seen_once": True, "gyro_age_ms": 100, "gyro_fresh": True, "device_connected": True, "stream_alive": True, "warning_flags": [], "error_flags": []}) + "\n", encoding="utf-8")
    (tmp_path / "b.jsonl").write_text(json.dumps({"session_id": "B", "now_ms": 1000, "attention": 65, "attention_seen_once": True, "attention_age_ms": 100, "attention_fresh": True, "gyro_x": 0.0, "gyro_y": 0.0, "gyro_z": 0.0, "gyro_seen_once": True, "gyro_age_ms": 100, "gyro_fresh": True, "device_connected": True, "stream_alive": True, "warning_flags": [], "error_flags": []}) + "\n", encoding="utf-8")
    (tmp_path / "a.frames.csv").write_text("session_id,frame_id,start_ms,end_ms,start_sec,end_sec,label,confidence,note\nA,0,0,2000,0,2,STABLE_FOCUS,low,\n", encoding="utf-8")
    (tmp_path / "b.frames.csv").write_text("session_id,frame_id,start_ms,end_ms,start_sec,end_sec,label,confidence,note\nB,0,0,2000,0,2,STABLE_FOCUS,low,\n", encoding="utf-8")
    cfg = tmp_path / "cfg.yaml"
    out = tmp_path / "out.json"
    report = tmp_path / "report.json"
    cfg.write_text(json.dumps({"fi_ema_alpha": 0.7}), encoding="utf-8")
    subprocess.run([sys.executable, "-m", "ui_cli.tune_task6b", "--input", str(tmp_path / "*.jsonl"), "--labels", str(tmp_path / "*.frames.csv"), "--base-config", str(cfg), "--trials", "5", "--method", "random", "--out", str(out), "--report", str(report)], check=True)
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["dataset_meta"]["input_files_count"] == 2
    assert payload["dataset_meta"]["label_files_count"] == 2
    assert payload["session_count"] == 2
    assert payload["total_labeled_frames"] == 2
    assert payload["top_candidates"]
