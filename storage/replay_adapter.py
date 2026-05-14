from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable


class ReplayAdapter:
    """JSONL 日志级回放适配器。

    当前仅支持事件级读取/过滤/回放/统计，不负责重新计算 FI/SQI。
    后续可扩展为“计算级重放”以复现估计链路。
    """
    def load_events(self, log_path: str) -> list[dict[str, Any]]:
        events = []
        for ln in Path(log_path).read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if not ln:
                continue
            events.append(json.loads(ln))
        return events

    def iter_events(self, log_path: str, event_types: set[str] | None = None):
        for e in self.load_events(log_path):
            et = e.get("event_type")
            if event_types and et not in event_types:
                continue
            yield e

    def replay(self, log_path: str, event_types: set[str] | None = None, speed: float = 0.0, on_event: Callable[[dict[str, Any]], None] | None = None) -> dict[str, Any]:
        start = time.time()
        last_ts = None
        count = 0
        by_type: dict[str, int] = {}
        for e in self.iter_events(log_path, event_types=event_types):
            ts = e.get("payload", {}).get("now_ms")
            if speed > 0 and last_ts is not None and ts is not None:
                delay = max(0.0, float(ts - last_ts) / 1000.0 / speed)
                if delay > 0:
                    time.sleep(delay)
            if ts is not None:
                last_ts = ts
            count += 1
            et = e.get("event_type", "unknown")
            by_type[et] = by_type.get(et, 0) + 1
            if on_event:
                on_event(e)
        return {"event_count": count, "event_type_counts": by_type, "elapsed_sec": time.time() - start}

    def summarize(self, log_path: str) -> dict[str, Any]:
        events = self.load_events(log_path)
        by_type: dict[str, int] = {}
        for e in events:
            et = e.get("event_type", "unknown")
            by_type[et] = by_type.get(et, 0) + 1
        return {"event_count": len(events), "event_type_counts": by_type}
