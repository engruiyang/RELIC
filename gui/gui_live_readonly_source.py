from __future__ import annotations

import threading
import time
from dataclasses import asdict
from typing import Any

from data.data_center import DataCenter
from relic_platform.platform_gateway import PlatformGateway


class GuiLiveReadonlySource:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000, poll_interval_sec: float = 0.1, gateway: PlatformGateway | None = None) -> None:
        self.host = host
        self.port = port
        self.poll_interval_sec = poll_interval_sec
        self._gateway = gateway or PlatformGateway(mode="live", host=host, port=port)
        self._data_center = DataCenter()
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

        self.connection_status = "disconnected"
        self.raw_message_count = 0
        self.decoded_attention_count = 0
        self.decoded_gyro_count = 0
        self.historical_warning_flags: set[str] = set()
        self.error_flags: set[str] = set()
        self.error_message: str | None = None

    def start(self) -> None:
        with self._lock:
            self.connection_status = "connecting"
        print(f"[GUI LIVE] connecting {self.host}:{self.port}", flush=True)
        try:
            self._gateway.start()
            with self._lock:
                self.connection_status = "connected"
                self.error_message = None
            print("[GUI LIVE] connected", flush=True)
        except Exception as exc:  # noqa: BLE001
            with self._lock:
                self.connection_status = "connect_failed"
                self.error_message = str(exc)
                self.error_flags.add("connect_failed")
            print(f"[GUI LIVE] connect_failed: {exc}", flush=True)
            return

        self._stop.clear()
        self._thread = threading.Thread(target=self._poll_loop, daemon=True, name="GuiLiveReadonlyPoll")
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        try:
            self._gateway.stop()
        except Exception as exc:  # noqa: BLE001
            with self._lock:
                self.error_flags.add("stop_failed")
                self.error_message = str(exc)
        with self._lock:
            if self.connection_status != "connect_failed":
                self.connection_status = "stopped"

    def _poll_loop(self) -> None:
        while not self._stop.is_set():
            try:
                now_ms = int(time.time() * 1000)
                events = self._gateway.poll_raw_events(now_ms)
                with self._lock:
                    self.raw_message_count += len(events)
                    for event in events:
                        if event.get("type") == "attention":
                            self.decoded_attention_count += 1
                        elif event.get("type") == "gyroscope":
                            self.decoded_gyro_count += 1
                self._data_center.ingest_events(events, now_ms)
                snap = self._data_center.get_runtime_snapshot()
                with self._lock:
                    self.historical_warning_flags.update(snap.get("warning_flags", []))
                    self.error_flags.update(snap.get("error_flags", []))
                health = self._gateway.health()
                if not health.get("alive", False) and self.connection_status == "connected":
                    with self._lock:
                        self.connection_status = "connection_closed_early"
                time.sleep(self.poll_interval_sec)
            except Exception as exc:  # noqa: BLE001
                with self._lock:
                    self.connection_status = "connection_closed_early"
                    self.error_flags.add("poll_loop_exception")
                    self.error_message = str(exc)
                return

    def get_runtime_snapshot(self) -> dict[str, Any]:
        snap = asdict(self._data_center.get_snapshot())
        warning_flags = list(snap.get("warning_flags") or [])
        if snap.get("attention_fresh"):
            warning_flags = [w for w in warning_flags if w != "attention_missing"]
        if snap.get("gyro_fresh"):
            warning_flags = [w for w in warning_flags if w != "gyro_missing"]

        with self._lock:
            return {
                "fi": float(snap.get("fi_smoothed") or 0.0),
                "sqi": float(snap.get("sqi") or 0.0),
                "attention": snap.get("attention"),
                "attention_age_ms": snap.get("attention_age_ms"),
                "attention_fresh": bool(snap.get("attention_fresh")),
                "gyro_x": snap.get("gyro_x"),
                "gyro_y": snap.get("gyro_y"),
                "gyro_z": snap.get("gyro_z"),
                "gyro_age_ms": snap.get("gyro_age_ms"),
                "gyro_fresh": bool(snap.get("gyro_fresh")),
                "stream_alive": bool(snap.get("stream_alive")),
                "connection_status": self.connection_status,
                "raw_message_count": self.raw_message_count,
                "decoded_attention_count": self.decoded_attention_count,
                "decoded_gyro_count": self.decoded_gyro_count,
                "current_warning_flags": warning_flags,
                "historical_warning_flags": sorted(self.historical_warning_flags),
                "error_flags": sorted(self.error_flags),
                "error_message": self.error_message,
                "source": "live_readonly",
            }

    def get_app_state(self) -> dict[str, Any]:
        runtime = self.get_runtime_snapshot()
        return {
            "state": "READY",
            "current_user_id": "",
            "current_user_name": "",
            "device_connected": runtime.get("connection_status") == "connected",
            "calibration_status": "unknown",
            "session_active": False,
            "current_game_id": "",
            "warning_flags": runtime.get("current_warning_flags", []),
            "error_flags": runtime.get("error_flags", []),
            "allowed_commands": ["refresh_snapshot", "load_demo_user", "end_session"],
            "source": "live_readonly",
            "connection_status": runtime.get("connection_status"),
        }

    def get_session_state(self) -> dict[str, Any]:
        return {
            "session_id": "",
            "user_id": "",
            "game_id": "",
            "session_active": False,
            "score": 0.0,
            "warning_count": 0,
            "error_count": 0,
            "log_path": "",
            "report_path": "",
            "platform_report_status": "",
            "source": "live_readonly",
        }

    def get_live_summary(self) -> dict[str, Any]:
        return self.get_runtime_snapshot()
