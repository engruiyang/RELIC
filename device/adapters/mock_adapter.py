class MockAdapter:
    def __init__(self, mode: str = "normal") -> None:
        self.mode = mode
        self.tick = 0
        self.connected = True

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def read(self) -> list[dict]:
        self.tick += 1
        events: list[dict] = [
            {"type": "device_status", "connected": self.connected},
            {"type": "stream_status", "alive": True, "active": True},
        ]

        if self.mode == "stream_drop" and self.tick >= 20:
            events[1] = {"type": "stream_status", "alive": False, "active": False}

        if self._should_emit_attention():
            events.append({"type": "attention", "value": 70 + (self.tick % 15)})

        if self._should_emit_gyro():
            k = float(self.tick)
            events.append({"type": "gyroscope", "x": 0.1 * k, "y": 0.2 * k, "z": -0.1 * k})

        return events

    def _should_emit_attention(self) -> bool:
        # ~1Hz when app tick is 20Hz
        if self.mode == "attention_missing_start":
            if self.tick <= 40:
                return False
        if self.mode == "attention_short_dropout":
            if 25 <= self.tick <= 65:
                return False
        if self.mode == "attention_long_lost":
            if self.tick >= 25:
                return False
        return self.tick % 20 == 0

    def _should_emit_gyro(self) -> bool:
        if self.mode == "gyro_short_dropout" and 15 <= self.tick <= 30:
            return False
        return True


    def poll(self, dt_ms: int | None = None) -> list[dict]:
        """Compatibility API for legacy callers/tests."""
        return self.read()
