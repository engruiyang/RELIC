from __future__ import annotations
import argparse, glob, json
from pathlib import Path
from ui_cli.evaluate_task6b import _load_jsonl, _load_labels, evaluate, load_structured_file

GYRO_SESSION_ID = "task6b_live_TEST_gyro_motion_001"


def _prediction_key(item: dict) -> str:
    return f"{item.get('session_id')}::{item.get('frame_id')}::{item.get('start_ms')}::{item.get('end_ms')}"


def _to_pred_map(report: dict) -> dict:
    return {_prediction_key(r): r.get("predicted_label") for r in report.get("frame_predictions", [])}


def _dist(rows: list[dict], key: str) -> dict:
    out = {}
    for r in rows:
        v = r.get(key)
        out[v] = out.get(v, 0) + 1
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--labels", required=True)
    p.add_argument("--base-config", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    input_paths = sorted(glob.glob(a.input))
    label_paths = sorted(glob.glob(a.labels))
    rows = _load_jsonl(input_paths)
    labels, label_meta = _load_labels(label_paths)
    base = load_structured_file(a.base_config)

    distracted = dict(base); distracted.update({"attention_low_fallback": 80, "attention_high_fallback": 90, "fi_ema_alpha": 0.4})
    stable = dict(base); stable.update({"attention_low_fallback": 10, "attention_high_fallback": 99, "fi_ema_alpha": 0.75})
    unreliable = dict(base); unreliable.update({"sqi_ok_threshold": 0.98, "sqi_invalid_threshold": 0.95})
    configs = {"base_config": base, "distracted_bias_config": distracted, "stable_bias_config": stable, "unreliable_bias_config": unreliable}

    reports = {n: evaluate(rows, labels, cfg, label_meta=label_meta) for n, cfg in configs.items()}
    names = list(reports)
    pairwise = {}
    warnings = []
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            k = f"{names[i]}__vs__{names[j]}"
            a_map, b_map = _to_pred_map(reports[names[i]]), _to_pred_map(reports[names[j]])
            c = sum(1 for kk in set(a_map)|set(b_map) if a_map.get(kk) != b_map.get(kk))
            pairwise[k] = c
            if c == 0:
                warnings.append("candidate config has no effect on predictions; check config propagation or evaluation path.")

    all_same = bool(pairwise) and all(v == 0 for v in pairwise.values())
    if all_same:
        warnings.append("config_propagation_or_evaluation_recompute_bug")

    base_rep = reports["base_config"]
    base_frames = [r for r in base_rep.get("frame_predictions", []) if r.get("session_id") == GYRO_SESSION_ID]
    base_mis = [r for r in base_rep.get("misclassified_frames", []) if r.get("session_id") == GYRO_SESSION_ID and r.get("true_label") == "UNRELIABLE_SIGNAL" and r.get("predicted_label") != "UNRELIABLE_SIGNAL"]
    q_fields = ["q_motion", "q_gyro", "gyro_rate_rms", "gyro_jitter_rms", "gyro_offset_rms", "sqi", "quality_state", "control_state"]
    available = sorted({k for r in base_mis for k, v in r.items() if k in q_fields and v not in (None, "")})
    missing = sorted(set(q_fields) - set(available))

    gyro_diag = {
        "session_id": GYRO_SESSION_ID,
        "true_unreliable_frames": sum(1 for r in base_frames if r.get("true_label") == "UNRELIABLE_SIGNAL"),
        "unreliable_miss": len(base_mis),
        "unreliable_miss_predicted_as": _dist(base_mis, "predicted_label"),
        "q_motion_distribution": [r.get("q_motion") for r in base_mis],
        "q_gyro_distribution": [r.get("q_gyro") for r in base_mis],
        "sqi_distribution": [r.get("sqi") for r in base_mis],
        "quality_state_distribution": _dist(base_mis, "quality_state"),
        "control_state_distribution": _dist(base_mis, "control_state"),
        "available_debug_fields": available,
        "missing_debug_fields": missing,
        "diagnosis": [],
    }
    if missing:
        gyro_diag["diagnosis"].append("missing_diagnostics_in_recorded_jsonl")
    qm = [v for v in gyro_diag["q_motion_distribution"] if isinstance(v, (int, float))]
    qg = [v for v in gyro_diag["q_gyro_distribution"] if isinstance(v, (int, float))]
    sqi = [v for v in gyro_diag["sqi_distribution"] if isinstance(v, (int, float))]
    if qm and qg and min(qm) > 0.6 and min(qg) > 0.6:
        gyro_diag["diagnosis"].append("imu_quality_feature_insensitive")
    if qm and qg and (min(qm) <= 0.6 or min(qg) <= 0.6) and (not sqi or min(sqi) > 0.6):
        gyro_diag["diagnosis"].append("sqi_aggregation_too_permissive")
    if gyro_diag["quality_state_distribution"] and any(k in ("invalid", "error") for k in gyro_diag["quality_state_distribution"]) and gyro_diag["control_state_distribution"].get("UNRELIABLE_SIGNAL", 0) == 0:
        gyro_diag["diagnosis"].append("control_state_gate_propagation_bug")
    if all_same:
        gyro_diag["diagnosis"].append("config_propagation_or_evaluation_recompute_bug")

    payload = {
        "dataset_meta": {
            "input_files_count": len(input_paths), "label_files_count": len(label_paths),
            "session_ids_from_logs": sorted({r.get("session_id") for r in rows if r.get("session_id")}),
            "session_ids_from_labels": sorted({l.get("session_id") for l in labels if l.get("session_id")}),
        },
        "configs": list(configs.keys()),
        "per_config_results": [{
            "name": n,
            "score": reports[n]["overall"].get("score"),
            "macro_f1": reports[n]["overall"].get("macro_f1"),
            "unreliable_miss": reports[n]["overall"].get("unreliable_miss"),
            "false_high_focus": reports[n]["overall"].get("false_high_focus"),
            "false_fatigue": reports[n]["overall"].get("false_fatigue"),
            "hard_rule_violation": reports[n]["overall"].get("hard_rule_violation"),
            "prediction_distribution": reports[n].get("prediction_distribution", {}),
            "per_session_scores": reports[n].get("per_session", []),
            "confusion_matrix": reports[n]["overall"].get("confusion_matrix", {}),
        } for n in names],
        "pairwise_changed_prediction_count": pairwise,
        "changed_prediction_count": pairwise,
        "warnings": warnings,
        "gyro_motion_diagnosis": gyro_diag,
    }
    Path(a.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))

if __name__ == '__main__':
    main()
