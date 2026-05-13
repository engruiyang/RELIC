from __future__ import annotations

import argparse
import csv
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


def load_structured_file(path: str) -> dict:
    text = Path(path).read_text(encoding="utf-8")
    if path.endswith(".json"):
        return json.loads(text)
    if yaml is not None:
        return yaml.safe_load(text) or {}
    if path.endswith(".yaml") or path.endswith(".yml"):
        out = {}
        for ln in text.splitlines():
            if ":" in ln and not ln.strip().startswith("-"):
                k, v = ln.split(":", 1)
                out[k.strip()] = v.strip().strip('"')
        if out:
            return out
        raise ValueError("Cannot parse YAML config. Please install PyYAML or use JSON config.")
    return json.loads(text)


def _load_labels(paths: list[str]) -> tuple[list[dict], dict]:
    if paths and paths[0].endswith(".frames.csv"):
        frames = []
        session_ids = set()
        for p in paths:
            with open(p, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    frames.append(row)
                    if row.get("session_id"):
                        session_ids.add(row.get("session_id"))
        return frames, {"mode": "frames", "session_ids": sorted(session_ids)}
    items = []
    for p in paths:
        data = load_structured_file(p)
        items.extend(data.get("segments", []))
    time_unit = "ms"
    session_ids = set()
    if paths:
        first = load_structured_file(paths[0])
        time_unit = first.get("time_unit", "ms")
        for p in paths:
            data = load_structured_file(p)
            if data.get("session_id"):
                session_ids.add(data.get("session_id"))
    return items, {"mode": "segments", "time_unit": time_unit, "session_ids": sorted(session_ids)}


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
    warning_count = 0
    skipped_rows = 0
    preds_by_session = {}
    for r in rows:
        try:
            t = int(r.get("now_ms", 0))
            gate = qg.evaluate(r, {"user_id": "offline"}, {"last_calibration_id": "offline"}, {"calibration_id": "offline", "valid": True, "device_id": "ipc_device", "attention_std": 1.0}, r.get("warning_flags", []), r.get("error_flags", []))
            s = dict(r) | gate
            fi = fe.estimate(s, {"attention_low_threshold": cfg.get("attention_low_fallback", 40), "attention_high_threshold": cfg.get("attention_high_fallback", 70)}, {"attention_baseline": 55, "attention_std": 1.0, "gyro_noise_rms": 0.5, "gyro_bias_x": 0, "gyro_bias_y": 0, "gyro_bias_z": 0})
            state = cs.evaluate(s, fi, tick_ms=1000).get("control_state")
        except Exception:  # noqa: BLE001
            skipped_rows += 1
            warning_count += 1
            continue
        sid = r.get("session_id")
        preds_by_session.setdefault(sid, []).append((t, state))
        label = _label_at(t, labels, (label_meta or {}).get("time_unit", "ms")) if (label_meta or {}).get("mode") != "frames" else None
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
    if (label_meta or {}).get("mode") == "frames":
        total = correct = 0
        confusion = {}
        false_fatigue = false_high = unreliable_miss = 0
        per_session_stats = {}
        for fr in labels:
            if fr.get("label") == "IGNORE":
                continue
            sid = fr.get("session_id")
            if sid not in preds_by_session:
                continue
            a, b = int(fr.get("start_ms", 0)), int(fr.get("end_ms", 0))
            in_frame = [s for t, s in preds_by_session.get(sid, []) if a <= int(t) < b]
            if not in_frame:
                continue
            counts = {}
            for s in in_frame:
                counts[s] = counts.get(s, 0) + 1
            best = sorted(counts.items(), key=lambda x: (x[1], in_frame[::-1].index(x[0])), reverse=True)[0][0]
            label = fr.get("label")
            total += 1
            correct += int(best == label)
            confusion.setdefault(label, {}).setdefault(best, 0)
            confusion[label][best] += 1
            if best == "FATIGUED" and label != "FATIGUED":
                false_fatigue += 1
            if best == "HIGH_FOCUS" and label != "HIGH_FOCUS":
                false_high += 1
            if label == "UNRELIABLE_SIGNAL" and best != "UNRELIABLE_SIGNAL":
                unreliable_miss += 1
            st = per_session_stats.setdefault(sid, {"total": 0, "correct": 0, "confusion": {}, "unreliable_miss": 0})
            st["total"] += 1
            st["correct"] += int(best == label)
            st["confusion"].setdefault(label, {}).setdefault(best, 0)
            st["confusion"][label][best] += 1
            if label == "UNRELIABLE_SIGNAL" and best != "UNRELIABLE_SIGNAL":
                st["unreliable_miss"] += 1
        transition_count = 0
    else:
        per_session_stats = {}
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
    score = 1.0 * macro_f1 - 0.3 * transition_jitter - 0.5 * latency_penalty - 2.0 * false_fatigue - 1.5 * false_high - 4.0 * unreliable_miss - 3.0 * hard_viol
    per_session = []
    if (label_meta or {}).get("mode") == "frames":
        for sid, st in sorted(per_session_stats.items(), key=lambda kv: (kv[0] is None, kv[0])):
            st_total = st["total"]
            st_correct = st["correct"]
            st_acc = (st_correct / st_total) if st_total else 0.0
            per_session.append({"session_id": sid, "total_labeled_frames": st_total, "frame_accuracy": st_acc, "confusion_matrix": st["confusion"], "unreliable_miss": st["unreliable_miss"]})
    else:
        per_session = [{"session_id": (rows[0].get("session_id") if rows else None), "total_labeled_frames": total, "frame_accuracy": acc, "macro_f1": macro_f1, "confusion_matrix": confusion, "score": score}]
    return {"overall": {"total_labeled_frames": total, "frame_accuracy": acc, "macro_f1": macro_f1, "confusion_matrix": confusion, "state_switches": transition_count, "transition_jitter": transition_jitter, "false_fatigue": false_fatigue, "false_high_focus": false_high, "unreliable_miss": unreliable_miss, "hard_rule_violation": hard_viol, "warning_count": warning_count, "skipped_rows": skipped_rows, "score": score}, "per_session": per_session}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--labels", required=True)
    p.add_argument("--config", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    input_paths = sorted(glob.glob(a.input))
    rows = _load_jsonl(input_paths)
    label_paths = sorted(glob.glob(a.labels))
    labels, label_meta = _load_labels(label_paths)
    cfg = load_structured_file(a.config)
    out = evaluate(rows, labels, cfg, label_meta=label_meta)
    log_sessions = sorted({r.get("session_id") for r in rows if r.get("session_id")})
    label_sessions = sorted({l.get("session_id") for l in labels if l.get("session_id")})
    matched = sorted(set(log_sessions) & set(label_sessions))
    out["dataset_meta"] = {
        "input_files_count": len(input_paths),
        "label_files_count": len(label_paths),
        "session_ids_from_logs": log_sessions,
        "session_ids_from_labels": label_sessions,
        "matched_session_ids": matched,
        "unmatched_log_sessions": sorted(set(log_sessions) - set(label_sessions)),
        "unmatched_label_sessions": sorted(set(label_sessions) - set(log_sessions)),
        "total_labeled_frames": out["overall"]["total_labeled_frames"],
    }
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
