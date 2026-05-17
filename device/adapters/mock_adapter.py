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
            events[1] = {"type": "stream_status", "alive": False, "active": False, "reason": "stream_drop"}
        if self.mode == "reconnect_recovery":
            if 30 <= self.tick <= 80:
                events[1] = {"type": "stream_status", "alive": False, "active": False, "reason": "stream_inactive"}
            elif self.tick > 80:
                events[1] = {"type": "stream_status", "alive": True, "active": True, "reason": "stream_recovered"}

        if self._should_emit_attention():
            att = 70 + (self.tick % 15)
            if self.mode == "missing_start" and self.tick <= 30:
                pass
            else:
                events.append({"type": "attention", "value": att})

        if self._should_emit_gyro():
            k = float(self.tick)
            gyro_event = {"type": "gyroscope", "x": 0.1 * k, "y": 0.2 * k, "z": -0.1 * k}
            if self.mode == "focus_jump" and self.tick % 5 == 0:
                gyro_event["quality_reasons"] = ["focus_jump"]
            if self.mode == "gyro_spike" and self.tick % 6 == 0:
                gyro_event["quality_reasons"] = list(gyro_event.get("quality_reasons", [])) + ["gyro_spike"]
            events.append(gyro_event)

        if self.mode == "partial_stale" and self.tick % 8 == 0:
            events.append({"type": "diagnostic", "quality_reasons": ["gyro_stale"]})

        return events

    def _should_emit_attention(self) -> bool:
        # ~1Hz when app tick is 20Hz
        if self.mode in {"attention_missing_start", "missing_start"}:
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


    def poll(self, dt_ms: int | None = None, mode: str | None = None) -> list[dict]:
        """Compatibility API for legacy callers/tests."""
        if mode:
            self.mode = mode
        return self.read()
