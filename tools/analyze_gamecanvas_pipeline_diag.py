from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from statistics import mean

MARKERS = [
    "[CANVAS CLICK DEBUG]",
    "[GAME INPUT DEBUG]",
    "[TRACELOCK HIT DEBUG]",
    "[RING DEBUG]",
    "[SHELL GAMEVIEW DEBUG]",
    "[CARD GAMEVIEW DEBUG]",
    "[CANVAS GAMEVIEW DEBUG]",
    "[CANVAS INSTANCE DEBUG]",
]

def read_text(path: Path) -> str:
    data = path.read_bytes()
    for enc in ("utf-8-sig", "utf-16", "utf-16-le", "gb18030"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="replace")

def json_objects_after_marker(text: str, marker: str) -> list[dict]:
    out = []
    idx = 0
    while True:
        pos = text.find(marker, idx)
        if pos < 0:
            break
        start = text.find("{", pos)
        if start < 0:
            idx = pos + len(marker)
            continue
        depth = 0
        in_str = False
        esc = False
        end = None
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
        if end is None:
            idx = start + 1
            continue
        raw = text[start:end]
        try:
            out.append(json.loads(raw))
        except json.JSONDecodeError:
            pass
        idx = end
    return out

def numbers(rows, key):
    vals = []
    for r in rows:
        val = r
        for part in key.split("."):
            if not isinstance(val, dict):
                val = None
                break
            val = val.get(part)
        if isinstance(val, (int, float)):
            vals.append(float(val))
    return vals

def summarize(name, vals):
    if not vals:
        return f"{name}: n=0"
    vals_sorted = sorted(vals)
    def pct(p):
        return vals_sorted[min(len(vals_sorted)-1, max(0, int(round((len(vals_sorted)-1)*p))))]
    return (
        f"{name}: n={len(vals)} min={vals_sorted[0]:.1f} "
        f"avg={mean(vals):.1f} p50={pct(0.5):.1f} p90={pct(0.9):.1f} max={vals_sorted[-1]:.1f}"
    )

def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python tools/analyze_gamecanvas_pipeline_diag.py logs/gamecanvas_diag.txt")
        return 2
    text = read_text(Path(sys.argv[1]))
    by_marker = {m: json_objects_after_marker(text, m) for m in MARKERS}
    print("counts:")
    for m, rows in by_marker.items():
        print(f"  {m}: {len(rows)}")

    clicks = by_marker["[CANVAS CLICK DEBUG]"]
    hits = by_marker["[TRACELOCK HIT DEBUG]"]
    rings = by_marker["[RING DEBUG]"]
    canvas_views = by_marker["[CANVAS GAMEVIEW DEBUG]"]
    cards = by_marker["[CARD GAMEVIEW DEBUG]"]
    shell = by_marker["[SHELL GAMEVIEW DEBUG]"]

    print()
    print(summarize("click.backend_age_ms", numbers(clicks, "backend_age_ms")))
    print(summarize("click.after_bridge_ms", numbers(clicks, "after_bridge_ms")))
    print(summarize("click.after_shell_ms", numbers(clicks, "after_shell_ms")))
    print(summarize("click.after_card_ms", numbers(clicks, "after_card_ms")))
    print(summarize("ring.backend_age_ms", numbers(rings, "backend_age_ms")))
    print(summarize("canvas_view.backend_age_ms", numbers(canvas_views, "backend_age_ms")))
    print(summarize("card.backend_age_ms", numbers(cards, "backend_age_ms")))
    print(summarize("shell.backend_age_ms", numbers(shell, "backend_age_ms")))

    # Pair clicks and backend hit diagnostics in order.
    pairs = list(zip(clicks, hits))
    frame_deltas = []
    time_left_deltas = []
    qml_candidate_backend_miss = 0
    target_mismatch = 0
    for c, h in pairs:
        cf = c.get("frame_id")
        hf = h.get("frame_id")
        if isinstance(cf, (int, float)) and isinstance(hf, (int, float)):
            frame_deltas.append(float(hf - cf))
        c_left = c.get("display_time_left_ms")
        h_left = h.get("time_left_ms")
        if isinstance(c_left, (int, float)) and isinstance(h_left, (int, float)):
            time_left_deltas.append(float(c_left - h_left))
        if c.get("display_hit_candidate") is True and h.get("final_hit") is False:
            qml_candidate_backend_miss += 1
        if c.get("display_target_id") and h.get("target_id") and c.get("display_target_id") != h.get("target_id"):
            target_mismatch += 1
    print()
    print(summarize("backend_frame_id - qml_frame_id", frame_deltas))
    print(summarize("qml_time_left_ms - backend_time_left_ms", time_left_deltas))
    print(f"qml_candidate_backend_miss={qml_candidate_backend_miss}")
    print(f"target_id_mismatch={target_mismatch}")

    instances = {}
    for r in rings + clicks + canvas_views:
        inst = r.get("canvas_instance_id") or r.get("instance") or "unknown"
        owner = r.get("debug_owner") or r.get("owner") or "unknown"
        instances.setdefault((inst, owner), 0)
        instances[(inst, owner)] += 1
    print()
    print("canvas_instances:")
    for (inst, owner), count in sorted(instances.items(), key=lambda kv: (-kv[1], kv[0][1])):
        print(f"  count={count} owner={owner} instance={inst}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
