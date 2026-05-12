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
    cfg = {}
    for k, (a, b) in SPACE.items():
        cfg[k] = random.uniform(a, b)
    return cfg


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
    rows = _load_jsonl(glob.glob(a.input))
    labels, label_meta = _load_labels(glob.glob(a.labels))
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
        keys = ("score", "macro_f1", "transition_jitter", "latency_penalty", "false_fatigue", "false_high_focus", "hard_rule_violation")
        results.append({"config": cfg, **{k: o.get(k, 0) for k in keys}})
    top = sorted(results, key=lambda x: x["score"], reverse=True)[:10]
    payload = {"top_candidates": top}
    Path(a.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if a.report:
        Path(a.report).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"top_candidates": top[:3]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
