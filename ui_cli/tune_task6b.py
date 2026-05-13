from __future__ import annotations

import argparse
import glob
import json
import random
from pathlib import Path

try:
    import yaml
except Exception:  # noqa: BLE001
    yaml = None

from ui_cli.evaluate_task6b import _load_jsonl, _load_labels, evaluate


SPACE = {
    "imu_rate_soft_mult": (5, 40),
    "imu_rate_bad_mult": (20, 160),
    "imu_jitter_soft_mult": (3, 30),
    "imu_jitter_bad_mult": (10, 120),
    "imu_offset_weight": (0.00, 0.10),
    "default_behavior_score": (0.55, 0.70),
    "fi_ema_alpha": (0.40, 0.75),
    "stable_enter": (55, 65),
    "stable_exit": (50, 60),
    "distracted_enter": (45, 58),
    "attention_low_fallback": (35, 45),
    "attention_high_fallback": (65, 78),
}


def _sample():
    while True:
        cfg = {}
        for k, (a, b) in SPACE.items():
            cfg[k] = random.uniform(a, b)
        if _validate(cfg):
            return cfg


def _validate(cfg: dict) -> bool:
    return (
        cfg["imu_rate_soft_mult"] < cfg["imu_rate_bad_mult"]
        and cfg["imu_jitter_soft_mult"] < cfg["imu_jitter_bad_mult"]
        and cfg["stable_exit"] <= cfg["stable_enter"]
        and cfg["distracted_enter"] < cfg["stable_enter"]
        and cfg["attention_low_fallback"] + 20 <= cfg["attention_high_fallback"]
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--labels", required=True)
    p.add_argument("--base-config", required=True)
    p.add_argument("--trials", type=int, default=300)
    p.add_argument("--method", choices=["random", "optuna"], default="random")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", required=True)
    p.add_argument("--report")
    a = p.parse_args()
    random.seed(a.seed)
    input_paths = sorted(glob.glob(a.input))
    label_paths = sorted(glob.glob(a.labels))
    rows = _load_jsonl(input_paths)
    labels, label_meta = _load_labels(label_paths)
    if yaml is None:
        base = json.loads(Path(a.base_config).read_text(encoding="utf-8"))
    else:
        base = yaml.safe_load(Path(a.base_config).read_text(encoding="utf-8")) or {}
    results = []
    for _ in range(a.trials):
        cfg = dict(base)
        cfg.update(_sample())
        r = evaluate(rows, labels, cfg, label_meta=label_meta)
        o = r["overall"]
        keys = ("score", "macro_f1", "transition_jitter", "latency_penalty", "false_fatigue", "false_high_focus", "hard_rule_violation", "unreliable_miss")
        results.append({"config": cfg, "validation": _validate(cfg), **{k: o.get(k, 0) for k in keys}})
    top = sorted(results, key=lambda x: x["score"], reverse=True)[:10]
    best_cfg = top[0]["config"] if top else dict(base)
    best_eval = evaluate(rows, labels, best_cfg, label_meta=label_meta)
    log_sessions = sorted({r.get("session_id") for r in rows if r.get("session_id")})
    label_sessions = sorted({l.get("session_id") for l in labels if l.get("session_id")})
    matched = sorted(set(log_sessions) & set(label_sessions))
    dataset_meta = {
        "input_files_count": len(input_paths),
        "label_files_count": len(label_paths),
        "session_ids_from_logs": log_sessions,
        "session_ids_from_labels": label_sessions,
        "matched_session_ids": matched,
        "unmatched_log_sessions": sorted(set(log_sessions) - set(label_sessions)),
        "unmatched_label_sessions": sorted(set(label_sessions) - set(log_sessions)),
        "total_labeled_frames": best_eval["overall"]["total_labeled_frames"],
    }
    warnings = []
    if label_meta.get("mode") == "frames" and dataset_meta["total_labeled_frames"] == 0:
        raise ValueError("No labeled frames matched between logs and labels.")
    if len(matched) < len(label_sessions):
        warnings.append("matched_session_ids less than label session count")
    if len(matched) == 1 and len(label_paths) > 1:
        warnings.append("only one session matched while multiple label files were provided")
    top_evals = [evaluate(rows, labels, c["config"], label_meta=label_meta) for c in top[:3]]
    if len(top_evals) >= 2:
        base_map = {(x.get("session_id"), x.get("frame_id"), x.get("start_ms"), x.get("end_ms")): x.get("predicted_label") for x in top_evals[0].get("frame_predictions", [])}
        same = True
        for rep in top_evals[1:]:
            cur = {(x.get("session_id"), x.get("frame_id"), x.get("start_ms"), x.get("end_ms")): x.get("predicted_label") for x in rep.get("frame_predictions", [])}
            if cur != base_map:
                same = False
                break
        if same:
            warnings.append("top candidate predictions are identical; tuning space may not affect current evaluation path.")
    payload = {
        "dataset_meta": dataset_meta,
        "session_count": len(matched),
        "total_labeled_frames": dataset_meta["total_labeled_frames"],
        "best_score": (top[0]["score"] if top else None),
        "top_candidates": top,
        "per_session_scores": best_eval.get("per_session", []),
        "unreliable_miss": best_eval["overall"].get("unreliable_miss", 0),
        "warnings": warnings,
    }
    Path(a.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if a.report:
        Path(a.report).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"top_candidates": top[:3]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
