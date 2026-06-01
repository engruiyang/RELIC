from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from typing import Any


PREFIXES = {
    "[CANVAS CLICK DEBUG]": "canvas_click",
    "[GAME INPUT DEBUG]": "game_input",
    "[TRACELOCK HIT DEBUG]": "hit_debug",
    "[RING DEBUG]": "ring",
}


def _json_after_prefix(line: str, prefix: str) -> dict[str, Any] | None:
    try:
        return json.loads(line.split(prefix, 1)[1].strip())
    except Exception:
        return None


def _avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _p95(values: list[float]) -> float | None:
    if not values:
        return None
    vals = sorted(values)
    idx = min(len(vals) - 1, int(round(0.95 * (len(vals) - 1))))
    return vals[idx]


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python tools/analyze_gamecanvas_diag_log.py <log.txt>")
        return 2

    path = Path(sys.argv[1])
    rows: dict[str, list[dict[str, Any]]] = {v: [] for v in PREFIXES.values()}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        for prefix, kind in PREFIXES.items():
            if prefix in line:
                item = _json_after_prefix(line, prefix)
                if item is not None:
                    rows[kind].append(item)

    clicks = rows["canvas_click"]
    inputs = rows["game_input"]
    hits = rows["hit_debug"]
    rings = rows["ring"]

    print("=== GameCanvas diagnostic summary ===")
    print(f"canvas_click={len(clicks)} game_input={len(inputs)} hit_debug={len(hits)} ring={len(rings)}")

    latencies = [float(x.get("delivery_latency_ms", 0)) for x in inputs if x.get("delivery_latency_ms") is not None]
    if latencies:
        print(f"delivery_latency_ms avg={_avg(latencies):.2f} p95={_p95(latencies):.2f} max={max(latencies):.2f}")

    candidate = [x for x in clicks if x.get("display_hit_candidate") is True]
    candidate_miss = []
    for idx, hit in enumerate(hits):
        qml = hit.get("qml_display") if isinstance(hit.get("qml_display"), dict) else {}
        if qml.get("display_hit_candidate") is True and hit.get("final_hit") is False:
            candidate_miss.append(hit)
    print(f"qml_hit_candidate={len(candidate)} qml_candidate_but_backend_miss={len(candidate_miss)}")

    mismatched_ids = []
    for hit in hits:
        qml = hit.get("qml_display") if isinstance(hit.get("qml_display"), dict) else {}
        qid = str(qml.get("display_target_id") or "")
        bid = str(hit.get("target_id") or "")
        if qid and bid and qid != bid:
            mismatched_ids.append((qid, bid))
    print(f"display_backend_target_id_mismatch={len(mismatched_ids)}")
    if mismatched_ids[:5]:
        print("first_id_mismatches=", mismatched_ids[:5])

    dist_deltas = []
    for hit in hits:
        qml = hit.get("qml_display") if isinstance(hit.get("qml_display"), dict) else {}
        qdist = qml.get("display_dist")
        bdist = hit.get("dist_current")
        if qdist is not None and bdist is not None:
            try:
                dist_deltas.append(abs(float(qdist) - float(bdist)))
            except Exception:
                pass
    if dist_deltas:
        print(f"abs(qml_display_dist-backend_dist_current) avg={_avg(dist_deltas):.5f} p95={_p95(dist_deltas):.5f} max={max(dist_deltas):.5f}")

    # Ring monotonicity: per target id, progress should generally decrease.
    ring_jumps = []
    prev_by_target: dict[str, float] = {}
    for r in rings:
        tid = str(r.get("target_id") or "")
        prog = r.get("ring_progress")
        if not tid or prog is None:
            continue
        try:
            prog_f = float(prog)
        except Exception:
            continue
        prev = prev_by_target.get(tid)
        if prev is not None:
            # Large upward jumps inside same target indicate local timer reset or model mismatch.
            if prog_f - prev > 0.08:
                ring_jumps.append({"target_id": tid, "prev": prev, "now": prog_f, "delta": prog_f - prev})
        prev_by_target[tid] = prog_f
    print(f"ring_progress_large_upward_jumps={len(ring_jumps)}")
    if ring_jumps[:5]:
        print("first_ring_jumps=", ring_jumps[:5])

    print("\nInterpretation hints:")
    print("- qml_candidate_but_backend_miss > 0: display coordinate or frame-time mismatch.")
    print("- target_id_mismatch > 0: GUI is showing a different target than backend is judging.")
    print("- large distance delta: normalization/play-field coordinate mismatch.")
    print("- ring upward jumps: local timer is being reset or ring row does not match target row.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
