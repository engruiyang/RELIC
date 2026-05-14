from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from data.data_center import DataCenter
from relic_platform.platform_gateway import PlatformGateway


class GatewayPort(Protocol):
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def health(self) -> dict[str, Any]: ...
    def poll_raw_events(self, now_ms: int) -> list[dict[str, Any]]: ...


@dataclass
class _Metrics:
    raw_message_count: int = 0
    decoded_attention_count: int = 0
    decoded_gyro_count: int = 0
    attention_first_seen_ms: int | None = None
    attention_last_seen_ms: int | None = None
    gyro_first_seen_ms: int | None = None
    gyro_last_seen_ms: int | None = None
    attention_intervals: list[int] = None  # type: ignore[assignment]
    gyro_intervals: list[int] = None  # type: ignore[assignment]
    attention_fresh_hits: int = 0
    gyro_fresh_hits: int = 0
    total_ticks: int = 0

    def __post_init__(self) -> None:
        if self.attention_intervals is None:
            self.attention_intervals = []
        if self.gyro_intervals is None:
            self.gyro_intervals = []


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--duration-sec", type=int, default=30)
    p.add_argument("--tick-ms", type=int, default=100)
    p.add_argument("--db-path", default="data/relic_local.db")
    p.add_argument("--output-dir", default="logs/live_stream_checks")
    p.add_argument("--save-jsonl", action="store_true")
    return p


def _interval_stats(values: list[int]) -> tuple[int | None, float | None, int | None]:
    if not values:
        return None, None, None
    return min(values), sum(values) / len(values), max(values)


def run_live_stream_check(
    host: str,
    port: int,
    duration_sec: int,
    db_path: str,
    output_dir: str,
    tick_ms: int = 100,
    save_jsonl: bool = False,
    gateway: GatewayPort | None = None,
) -> dict[str, Any]:
    _ = db_path
    now_ms = int(time.time() * 1000)
    out_path: Path | None = None
    metrics = _Metrics()
    data_center = DataCenter()
    warning_flags: set[str] = set()
    error_flags: set[str] = set()

    gw = gateway or PlatformGateway(mode="live", host=host, port=port)
    writer = None
    if save_jsonl:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"live_stream_check_{now_ms}.jsonl"
        writer = out_path.open("w", encoding="utf-8")

    try:
        gw.start()
    except Exception as exc:  # noqa: BLE001
        return {
            "mode": "live_stream_check",
            "host": host,
            "port": port,
            "duration_sec": duration_sec,
            "raw_message_count": 0,
            "decoded_attention_count": 0,
            "decoded_gyro_count": 0,
            "attention_interval_ms_min": None,
            "attention_interval_ms_avg": None,
            "attention_interval_ms_max": None,
            "gyro_interval_ms_min": None,
            "gyro_interval_ms_avg": None,
            "gyro_interval_ms_max": None,
            "last_attention": None,
            "last_gyro": None,
            "attention_age_ms": None,
            "gyro_age_ms": None,
            "attention_fresh_ratio": 0.0,
            "gyro_fresh_ratio": 0.0,
            "stream_alive": False,
            "warning_count": 0,
            "error_count": 1,
            "warning_flags": [],
            "error_flags": ["connect_failed"],
            "error_message": str(exc),
            "output_log_path": str(out_path) if out_path else None,
        }

    start = time.monotonic()
    deadline = start + max(1, duration_sec)
    try:
        while time.monotonic() < deadline:
            loop_now_ms = int(time.time() * 1000)
            metrics.total_ticks += 1
            events = gw.poll_raw_events(loop_now_ms)
            metrics.raw_message_count += len(events)

            for event in events:
                event_type = event.get("type")
                if event_type == "attention":
                    metrics.decoded_attention_count += 1
                    prev = metrics.attention_last_seen_ms
                    if metrics.attention_first_seen_ms is None:
                        metrics.attention_first_seen_ms = loop_now_ms
                    if prev is not None:
                        metrics.attention_intervals.append(loop_now_ms - prev)
                    metrics.attention_last_seen_ms = loop_now_ms
                elif event_type == "gyroscope":
                    metrics.decoded_gyro_count += 1
                    prev = metrics.gyro_last_seen_ms
                    if metrics.gyro_first_seen_ms is None:
                        metrics.gyro_first_seen_ms = loop_now_ms
                    if prev is not None:
                        metrics.gyro_intervals.append(loop_now_ms - prev)
                    metrics.gyro_last_seen_ms = loop_now_ms

            data_center.ingest_events(events, loop_now_ms)
            snap = data_center.get_runtime_snapshot()

            if snap.get("attention_fresh"):
                metrics.attention_fresh_hits += 1
            if snap.get("gyro_fresh"):
                metrics.gyro_fresh_hits += 1

            warning_flags.update(snap.get("warning_flags", []))
            error_flags.update(snap.get("error_flags", []))

            if writer is not None:
                writer.write(json.dumps({"now_ms": loop_now_ms, "events": events, "snapshot": snap}, ensure_ascii=False) + "\n")
            time.sleep(max(0.01, tick_ms / 1000.0))
    except Exception as exc:  # noqa: BLE001
        error_flags.add("runtime_exception")
        warning_flags.add("stream_check_interrupted")
        runtime_exception = str(exc)
    else:
        runtime_exception = None
    finally:
        gw.stop()
        if writer is not None:
            writer.close()

    snap = data_center.get_runtime_snapshot()
    a_min, a_avg, a_max = _interval_stats(metrics.attention_intervals)
    g_min, g_avg, g_max = _interval_stats(metrics.gyro_intervals)

    if metrics.decoded_attention_count == 0 and metrics.decoded_gyro_count > 0:
        warning_flags.add("attention_stale")
    if metrics.raw_message_count == 0:
        error_flags.add("no_data")

    summary = {
        "mode": "live_stream_check",
        "host": host,
        "port": port,
        "duration_sec": duration_sec,
        "raw_message_count": metrics.raw_message_count,
        "decoded_attention_count": metrics.decoded_attention_count,
        "decoded_gyro_count": metrics.decoded_gyro_count,
        "attention_first_seen_ms": metrics.attention_first_seen_ms,
        "attention_last_seen_ms": metrics.attention_last_seen_ms,
        "gyro_first_seen_ms": metrics.gyro_first_seen_ms,
        "gyro_last_seen_ms": metrics.gyro_last_seen_ms,
        "attention_interval_ms_min": a_min,
        "attention_interval_ms_avg": a_avg,
        "attention_interval_ms_max": a_max,
        "gyro_interval_ms_min": g_min,
        "gyro_interval_ms_avg": g_avg,
        "gyro_interval_ms_max": g_max,
        "last_attention": snap.get("attention"),
        "last_gyro": {"x": snap.get("gyro_x"), "y": snap.get("gyro_y"), "z": snap.get("gyro_z")},
        "attention_age_ms": snap.get("attention_age_ms"),
        "gyro_age_ms": snap.get("gyro_age_ms"),
        "attention_fresh_ratio": 0.0 if metrics.total_ticks == 0 else metrics.attention_fresh_hits / metrics.total_ticks,
        "gyro_fresh_ratio": 0.0 if metrics.total_ticks == 0 else metrics.gyro_fresh_hits / metrics.total_ticks,
        "stream_alive": bool(gw.health().get("alive", False) or snap.get("stream_alive", False)),
        "warning_count": len(warning_flags),
        "error_count": len(error_flags),
        "warning_flags": sorted(warning_flags),
        "error_flags": sorted(error_flags),
        "error_message": runtime_exception,
        "output_log_path": str(out_path) if out_path else None,
    }
    return summary


def main() -> None:
    args = build_parser().parse_args()
    summary = run_live_stream_check(
        host=args.host,
        port=args.port,
        duration_sec=args.duration_sec,
        db_path=args.db_path,
        output_dir=args.output_dir,
        tick_ms=args.tick_ms,
        save_jsonl=args.save_jsonl,
    )
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
