from __future__ import annotations

import inspect
import math
import threading
import time
from typing import Any, Protocol


class DataBridgeProtocol(Protocol):
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def get_snapshot(self) -> dict: ...
    def close(self) -> None: ...


class LiveDataBridgeAdapter:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000, **kwargs: Any):
        self.host = host
        self.port = port
        self.kwargs = kwargs
        self.client: Any | None = None
        self._thread: threading.Thread | None = None
        self._thread_error: Exception | None = None
        self._alive = False

    def _build_client(self, cls: type) -> Any:
        sig = inspect.signature(cls.__init__)
        defaults = {
            "host": self.host,
            "port": self.port,
            "print_attention": False,
            "verbose": False,
            "dump_raw": False,
            "raw_limit": 0,
            "save_payload_text": False,
        }
        args = {}
        for name in list(sig.parameters.keys())[1:]:
            if name in self.kwargs:
                args[name] = self.kwargs[name]
            elif name in defaults:
                args[name] = defaults[name]
        return cls(**args)

    def start(self) -> None:
        err: Exception | None = None
        cls = None
        for mod in ("relic_data_bridge", "RELIC_MAIN"):
            try:
                m = __import__(mod, fromlist=["RelicClient"])
                cls = getattr(m, "RelicClient")
                break
            except Exception as exc:
                err = exc
        if cls is None:
            raise RuntimeError(f"无法导入RelicClient: {err}")
        self.client = self._build_client(cls)
        self.client.connect()
        self._alive = True
        self._thread_error = None

        def _run() -> None:
            try:
                self.client.recv_loop()
            except Exception as exc:  # noqa: BLE001
                self._thread_error = exc
            finally:
                self._alive = False
                if self.client is not None and hasattr(self.client, "connected"):
                    self.client.connected = False

        self._thread = threading.Thread(target=_run, daemon=True, name="LiveDataBridgeRecv")
        self._thread.start()

    def is_alive(self) -> bool:
        return bool(self._alive and self._thread and self._thread.is_alive())

    def stop(self) -> None:
        self._alive = False
        if self.client and hasattr(self.client, "close"):
            self.client.close()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _augment_snapshot(self, raw: dict[str, Any]) -> dict[str, Any]:
        now_ms = int(time.monotonic() * 1000)
        snap = dict(raw)
        if self.client is not None:
            for k in ("focus_area_x", "focus_area_y", "focus_area_width", "focus_area_height"):
                if k not in snap:
                    snap[k] = getattr(self.client, k, None)
            if snap.get("attention_age_ms") is None and getattr(self.client, "attention_ts_ms", None) is not None:
                snap["attention_age_ms"] = now_ms - int(self.client.attention_ts_ms)
            if snap.get("gyro_age_ms") is None and getattr(self.client, "gyro_ts_ms", None) is not None:
                snap["gyro_age_ms"] = now_ms - int(self.client.gyro_ts_ms)
        snap["bridge_alive"] = self.is_alive()
        if not snap["bridge_alive"]:
            snap["connected"] = False
        return snap

    def get_snapshot(self) -> dict:
        if self.client is None:
            return {"connected": False, "bridge_alive": False}
        raw = self.client.get_snapshot()
        if not isinstance(raw, dict):
            raw = {}
        return self._augment_snapshot(raw)

    def close(self) -> None:
        self.stop()


class MockDataBridge:
    def __init__(self):
        self.running = False
        self.t0 = time.monotonic()
        self.last_att = self.t0
        self.last_gyro = self.t0
        self.att = 60
        self.s = {"connected": True, "attention_valid": True, "gyro_valid": True}

    def start(self) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False
        self.s["connected"] = False

    def is_alive(self) -> bool:
        return self.running

    def tick(self, dt_ms: int = 50) -> None:
        n = time.monotonic()
        t = n - self.t0
        if (n - self.last_gyro) >= 0.05:
            self.s.update({
                "focus_area_x": 0.0,
                "focus_area_y": 0.0,
                "focus_area_width": 1920.0,
                "focus_area_height": 1080.0,
                "focus_x": 960 + 220 * math.sin(t / 2),
                "focus_y": 540 + 120 * math.cos(t / 2),
                "gyro_x": 255 + 10 * math.sin(t),
                "gyro_y": 255 + 8 * math.cos(t * 1.2),
                "gyro_z": 176 + 6 * math.sin(t * 0.7),
                "gyro_age_ms": 0,
                "gyro_valid": True,
            })
            self.last_gyro = n
        else:
            self.s["gyro_age_ms"] = int((n - self.last_gyro) * 1000)

        if (n - self.last_att) >= 1.0:
            self.att = max(0, min(100, self.att + int(5 * math.sin(t))))
            self.s.update({"attention_value": self.att, "attention_valid": True, "attention_age_ms": 0})
            self.last_att = n
        else:
            self.s["attention_age_ms"] = int((n - self.last_att) * 1000)

    def get_snapshot(self) -> dict:
        if self.running:
            self.s["connected"] = True
            self.tick()
        return {**self.s, "bridge_alive": self.running}

    def close(self) -> None:
        self.stop()
