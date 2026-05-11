from __future__ import annotations

from device.adapters.mock_adapter import MockAdapter
from relic_platform.platform_messages import PlatformMessageParser


class PlatformGateway:
    def __init__(self, mode: str = "mock", host: str = "127.0.0.1", port: int = 8000):
        self.mode = mode
        self.host = host
        self.port = port
        self._parser = PlatformMessageParser()
        self._mock_adapter = MockAdapter(mode="normal")
        self._live_bridge = None

    def start(self) -> None:
        if self.mode == "mock":
            self._mock_adapter.connect()
            return

        from relic_core.bridge_adapter import LiveDataBridgeAdapter

        self._live_bridge = LiveDataBridgeAdapter(host=self.host, port=self.port)
        self._live_bridge.start()

    def stop(self) -> None:
        if self.mode == "mock":
            self._mock_adapter.disconnect()
            return
        if self._live_bridge is not None:
            self._live_bridge.close()

    def health(self) -> dict:
        if self.mode == "mock":
            return {"connected": True, "alive": True}
        if self._live_bridge is None:
            return {"connected": False, "alive": False}
        snap = self._live_bridge.get_snapshot() or {}
        return {
            "connected": bool(snap.get("connected", False)),
            "alive": bool(snap.get("bridge_alive", self._live_bridge.is_alive())),
        }

    def poll_raw_events(self, now_ms: int) -> list[dict]:
        if self.mode == "mock":
            return self._mock_adapter.read()

        if self._live_bridge is None:
            return []
        payload = self._live_bridge.get_snapshot() or {}
        return self._parser.to_raw_events(payload=payload, now_ms=now_ms)
