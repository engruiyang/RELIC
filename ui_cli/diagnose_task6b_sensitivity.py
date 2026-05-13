from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

from ui_cli.evaluate_task6b import _load_jsonl, _load_labels, evaluate, load_structured_file


def _prediction_key(item: dict) -> str:
    return f"{item.get('session_id')}::{item.get('frame_id')}::{item.get('start_ms')}::{item.get('end_ms')}"


def _to_pred_map(report: dict) -> dict:
    out = {}
    for row in report.get("misclassified_frames", []):
        out[_prediction_key(row)] = row.get("predicted_label")
    return out


def _changed_count(a_report: dict, b_report: dict) -> int:
    a = _to_pred_map(a_report)
    b = _to_pred_map(b_report)
    keys = set(a) | set(b)
    return sum(1 for k in keys if a.get(k) != b.get(k))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--labels", required=True)
    p.add_argument("--base-config", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--gyro-out", default="reports/task6b_gyro_motion_diagnosis.json")
    a = p.parse_args()

    rows = _load_jsonl(sorted(glob.glob(a.input)))
    labels, label_meta = _load_labels(sorted(glob.glob(a.labels)))
    base = load_structured_file(a.base_config)

    low = dict(base)
    low.update({"fi_ema_alpha": 0.4, "attention_low_fallback": 70, "attention_high_fallback": 75, "sqi_ok_threshold": 0.95, "sqi_invalid_threshold": 0.90})
    high = dict(base)
    high.update({"fi_ema_alpha": 0.75, "attention_low_fallback": 20, "attention_high_fallback": 95, "sqi_ok_threshold": 0.4, "sqi_invalid_threshold": 0.2})

    candidates = {"base": base, "extreme_low_threshold": low, "extreme_high_threshold": high}
    reports = {}
    for name, cfg in candidates.items():
        reports[name] = evaluate(rows, labels, cfg, label_meta=label_meta)

    names = list(reports.keys())
    changed = {}
    warnings = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            k = f"{names[i]}__vs__{names[j]}"
            c = _changed_count(reports[names[i]], reports[names[j]])
            changed[k] = c
            if c == 0:
                warnings.append(f"{k}: candidate config has no effect on predictions; check config propagation or evaluation path.")

    payload = {
        "configs": {n: {
            "overall": {
                "macro_f1": reports[n]["overall"].get("macro_f1"),
                "score": reports[n]["overall"].get("score"),
                "unreliable_miss": reports[n]["overall"].get("unreliable_miss"),
            },
            "per_session": reports[n].get("per_session", []),
            "prediction_distribution": reports[n].get("prediction_distribution", {}),
        } for n in names},
        "changed_prediction_count": changed,
        "warnings": warnings,
    }
    Path(a.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    base_mis = reports["base"].get("misclassified_frames", [])
    gyro_miss = [r for r in base_mis if r.get("session_id") == "task6b_live_TEST_gyro_motion_001" and r.get("true_label") == "UNRELIABLE_SIGNAL" and r.get("predicted_label") != "UNRELIABLE_SIGNAL"]
    gyro_true_unrel = [
        r for r in reports["base"].get("per_session", [])
        if r.get("session_id") == "task6b_live_TEST_gyro_motion_001"
    ]
    values = lambda rows, k: [x.get(k) for x in rows if isinstance(x.get(k), (int, float))]
    q_motion_vals = values(gyro_miss, "q_motion")
    q_gyro_vals = values(gyro_miss, "q_gyro")
    sqi_vals = values(gyro_miss, "sqi")
    gyro_diag = {
        "session_id": "task6b_live_TEST_gyro_motion_001",
        "true_unreliable_frames_total": sum(sum(v.values()) for s in gyro_true_unrel for k, v in s.get("confusion_matrix", {}).items() if k == "UNRELIABLE_SIGNAL"),
        "unreliable_miss_frames": len(gyro_miss),
        "q_motion_distribution": q_motion_vals,
        "q_gyro_distribution": q_gyro_vals,
        "sqi_distribution": sqi_vals,
        "gyro_rate_rms_distribution": values(gyro_miss, "gyro_rate_rms"),
        "gyro_jitter_rms_distribution": values(gyro_miss, "gyro_jitter_rms"),
        "gyro_offset_rms_distribution": values(gyro_miss, "gyro_offset_rms"),
    }
    if q_motion_vals and q_gyro_vals and min(q_motion_vals) > 0.6 and min(q_gyro_vals) > 0.6:
        gyro_diag["diagnosis"] = "IMU quality feature insensitive"
    elif q_motion_vals and q_gyro_vals:
        gyro_diag["diagnosis"] = "SQI aggregation too permissive"
    else:
        gyro_diag["diagnosis"] = "control state gate propagation bug"
    Path(a.gyro_out).write_text(json.dumps(gyro_diag, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
