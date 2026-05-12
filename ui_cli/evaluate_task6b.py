from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

try:
    import yaml
except Exception:  # noqa: BLE001
    yaml = None

from core.quality_gate import QualityGate
from core.focus_estimator import FocusEstimator
from core.control_state_estimator import ControlStateEstimator


def _load_jsonl(paths: list[str]) -> list[dict]:
    rows = []
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def _load_labels(paths: list[str]) -> list[dict]:
    items = []
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            if yaml is None:
                data = json.loads(f.read())
            else:
                data = yaml.safe_load(f) or {}
            items.extend(data.get("segments", []))
    return items


def _label_at(ts: int, segments: list[dict], time_unit: str = "ms") -> str | None:
    for s in segments:
        if "start_ms" in s:
            a, b = int(s.get("start_ms", 0)), int(s.get("end_ms", 0))
        else:
            mul = 1000 if time_unit == "sec" else 1
            a, b = int(float(s.get("start", 0)) * mul), int(float(s.get("end", 0)) * mul)
        if a <= ts <= b:
            return s.get("label")
    return None


def evaluate(rows: list[dict], labels: list[dict], cfg: dict, label_meta: dict | None = None) -> dict:
    qg = QualityGate(sqi_ok_threshold=cfg.get("sqi_ok_threshold", 0.75), sqi_invalid_threshold=cfg.get("sqi_invalid_threshold", 0.60))
    fe = FocusEstimator(alpha=cfg.get("fi_ema_alpha", 0.7))
    cs = ControlStateEstimator()
    confusion = {}
    correct = total = 0
    false_fatigue = false_high = unreliable_miss = hard_viol = 0
    prev_state = None
    transition_count = 0
    for r in rows:
        t = int(r.get("now_ms", 0))
        gate = qg.evaluate(r, {"user_id": "offline"}, {"last_calibration_id": "offline"}, {"calibration_id": "offline", "valid": True, "device_id": "ipc_device", "attention_std": 1.0}, r.get("warning_flags", []), r.get("error_flags", []))
        s = dict(r) | gate
        fi = fe.estimate(s, {"attention_low_threshold": cfg.get("attention_low_fallback", 40), "attention_high_threshold": cfg.get("attention_high_fallback", 70)}, {"attention_baseline": 55, "attention_std": 1.0, "gyro_noise_rms": 0.5, "gyro_bias_x": 0, "gyro_bias_y": 0, "gyro_bias_z": 0})
        state = cs.evaluate(s, fi, tick_ms=1000).get("control_state")
        label = _label_at(t, labels, (label_meta or {}).get("time_unit", "ms"))
        if label == "IGNORE":
            continue
        if label:
            total += 1
            correct += int(label == state)
            confusion.setdefault(label, {}).setdefault(state, 0)
            confusion[label][state] += 1
            if state == "FATIGUED" and label != "FATIGUED":
                false_fatigue += 1
            if state == "HIGH_FOCUS" and label != "HIGH_FOCUS":
                false_high += 1
            if label != "UNRELIABLE_SIGNAL" and state == "UNRELIABLE_SIGNAL":
                unreliable_miss += 1
        if prev_state is not None and prev_state != state:
            transition_count += 1
        prev_state = state
        if state == "FATIGUED" and ("attention_lost" in s.get("quality_reasons", []) or "gyro_lost" in s.get("quality_reasons", []) or "stream_dead" in s.get("quality_reasons", [])):
            hard_viol += 1
    acc = (correct / total) if total else 0.0
    per_f1 = []
    classes = set(confusion.keys()) | {p for d in confusion.values() for p in d.keys()}
    for c in classes:
        tp = confusion.get(c, {}).get(c, 0)
        fp = sum(confusion.get(o, {}).get(c, 0) for o in classes if o != c)
        fn = sum(v for k, v in confusion.get(c, {}).items() if k != c)
        prec = tp / max(tp + fp, 1)
        rec = tp / max(tp + fn, 1)
        per_f1.append(0.0 if (prec + rec) == 0 else 2 * prec * rec / (prec + rec))
    macro_f1 = sum(per_f1) / max(len(per_f1), 1)
    transition_jitter = transition_count / max(total, 1)
    latency_penalty = 0.0
    score = 1.0 * macro_f1 - 0.3 * transition_jitter - 0.5 * latency_penalty - 2.0 * false_fatigue - 1.5 * false_high - 3.0 * hard_viol
    return {"confusion_matrix": confusion, "state_accuracy": acc, "macro_f1": macro_f1, "state_switches": transition_count, "avg_latency": 0.0, "hard_rule_violation": hard_viol, "false_fatigue": false_fatigue, "false_high_focus": false_high, "unreliable_miss": unreliable_miss, "transition_jitter": transition_jitter, "latency_penalty": latency_penalty, "score": score}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--labels", required=True)
    p.add_argument("--config", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    rows = _load_jsonl(glob.glob(a.input))
    label_paths = glob.glob(a.labels)
    labels = _load_labels(label_paths)
    label_meta = {}
    if label_paths:
        txt = Path(label_paths[0]).read_text(encoding="utf-8")
        meta = json.loads(txt) if yaml is None else (yaml.safe_load(txt) or {})
        label_meta = {"session_id": meta.get("session_id"), "time_unit": meta.get("time_unit", "ms")}
    if yaml is None:
        cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    else:
        cfg = yaml.safe_load(Path(a.config).read_text(encoding="utf-8")) or {}
    if label_meta.get("session_id"):
        rows = [r for r in rows if r.get("session_id") == label_meta["session_id"]]
    out = evaluate(rows, labels, cfg, label_meta=label_meta)
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
