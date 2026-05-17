from __future__ import annotations

from dataclasses import asdict

from data.realtime_snapshot import RealtimeSnapshot


class DataCenter:
    def __init__(
        self,
        attention_fresh_ms: int = 1500,
        attention_lost_ms: int = 5000,
        gyro_fresh_ms: int = 500,
        gyro_lost_ms: int = 2000,
    ) -> None:
        self._snapshot = RealtimeSnapshot()
        self._attention_fresh_ms = attention_fresh_ms
        self._attention_lost_ms = attention_lost_ms
        self._gyro_fresh_ms = gyro_fresh_ms
        self._gyro_lost_ms = gyro_lost_ms
        self._event_quality_reasons: list[str] = []
        self._valid_signal_frames: int = 0
        self._last_valid_frame_key: tuple[int | None, int | None] | None = None
        self._warmup_frames_required: int = 5

    def ingest_events(self, events: list[dict], now_ms: int) -> None:
        self._snapshot.now_ms = now_ms
        self._event_quality_reasons = []
        for event in events:
            self._apply_event(event, now_ms)
        self._refresh_derived_flags(now_ms)

    def get_snapshot(self) -> RealtimeSnapshot:
        return self._snapshot

    def get_runtime_snapshot(self) -> dict:
        return asdict(self._snapshot) | {"gyro": self._snapshot.gyro}

    def apply_quality_gate(self, gate_result: dict) -> None:
        self._snapshot.sqi = float(gate_result.get("sqi", 0.0))
        self._snapshot.quality_state = str(gate_result.get("quality_state", "error"))
        self._snapshot.quality_reasons = list(gate_result.get("quality_reasons", []))
        self._snapshot.calibration_usable = bool(gate_result.get("calibration_usable", False))
        self._snapshot.formal_training_allowed = bool(gate_result.get("formal_training_allowed", False))
        self._snapshot.signal_reliable = bool(gate_result.get("signal_reliable", False))
        self._snapshot.estimation_allowed = bool(gate_result.get("estimation_allowed", False))

    def _append_event_reasons(self, event: dict) -> None:
        reasons = []

        if isinstance(event.get("quality_reasons"), list):
            reasons.extend(str(x) for x in event.get("quality_reasons", []))

        if event.get("quality_reason") is not None:
            reasons.append(str(event.get("quality_reason")))

        if isinstance(event.get("warning_flags"), list):
            reasons.extend(str(x) for x in event.get("warning_flags", []))

        if isinstance(event.get("error_flags"), list):
            reasons.extend(str(x) for x in event.get("error_flags", []))

        if event.get("reason") is not None:
            reasons.append(str(event.get("reason")))

        for reason in reasons:
            if reason and reason not in self._event_quality_reasons:
                self._event_quality_reasons.append(reason)

    def _apply_event(self, event: dict, now_ms: int) -> None:
        self._append_event_reasons(event)
        event_type = event.get("type")

        if event_type == "device_status":
            connected_raw = event.get("connected", event.get("device_connected", False))
            self._snapshot.device_connected = bool(connected_raw)

            if "stream_alive" in event:
                self._snapshot.stream_alive = bool(event.get("stream_alive"))
            elif "bridge_alive" in event:
                self._snapshot.stream_alive = bool(event.get("bridge_alive"))

            if "sensor_stream_active" in event:
                self._snapshot.sensor_stream_active = bool(event.get("sensor_stream_active"))
            elif "bridge_alive" in event:
                self._snapshot.sensor_stream_active = bool(event.get("bridge_alive"))

            if not self._snapshot.device_connected:
                self._snapshot.stream_alive = False
                self._snapshot.sensor_stream_active = False

        elif event_type == "stream_status":
            self._snapshot.stream_alive = bool(event.get("alive", False))
            self._snapshot.sensor_stream_active = bool(event.get("active", False))

        elif event_type == "attention":
            self._snapshot.attention = event.get("value")
            self._snapshot.attention_last_update_ms = now_ms
            self._snapshot.attention_seen_once = True

        elif event_type == "gyroscope":
            self._snapshot.gyro_x = event.get("x")
            self._snapshot.gyro_y = event.get("y")
            self._snapshot.gyro_z = event.get("z")
            self._snapshot.gyro_last_update_ms = now_ms
            self._snapshot.gyro_seen_once = True
            self._snapshot.focus_seen_once = True

        elif event_type == "algorithm_frame":
            algo = str(event.get("algorithm") or "")
            data = event.get("data") or {}

            if algo == "attention":
                self._snapshot.attention = data.get("attention")
                self._snapshot.attention_last_update_ms = now_ms
                self._snapshot.attention_seen_once = True

            elif algo == "gyroscope":
                self._snapshot.gyro_x = data.get("gyro_x", data.get("focus_x"))
                self._snapshot.gyro_y = data.get("gyro_y", data.get("focus_y"))
                self._snapshot.gyro_z = data.get("gyro_z")
                self._snapshot.gyro_last_update_ms = now_ms
                self._snapshot.gyro_seen_once = True
                self._snapshot.focus_seen_once = True

    def _refresh_derived_flags(self, now_ms: int) -> None:
        s = self._snapshot
        s.warning_flags = []
        s.error_flags = []
        s.quality_reasons = list(self._event_quality_reasons)

        if s.attention_last_update_ms is None:
            s.attention_age_ms = None
            s.attention_fresh = False
            s.warning_flags.append("attention_missing")
        else:
            s.attention_age_ms = now_ms - s.attention_last_update_ms
            if s.attention_age_ms <= self._attention_fresh_ms:
                s.attention_fresh = True
            elif s.attention_age_ms <= self._attention_lost_ms:
                s.attention_fresh = False
                s.warning_flags.append("attention_stale")
                if "attention_stale" not in s.quality_reasons:
                    s.quality_reasons.append("attention_stale")
            else:
                s.attention_fresh = False
                s.error_flags.append("attention_lost")
                if "attention_lost" not in s.quality_reasons:
                    s.quality_reasons.append("attention_lost")

        if s.gyro_last_update_ms is None:
            s.gyro_age_ms = None
            s.gyro_fresh = False
            s.warning_flags.append("gyro_missing")
        else:
            s.gyro_age_ms = now_ms - s.gyro_last_update_ms
            if s.gyro_age_ms <= self._gyro_fresh_ms:
                s.gyro_fresh = True
            elif s.gyro_age_ms <= self._gyro_lost_ms:
                s.gyro_fresh = False
                s.warning_flags.append("gyro_stale")
                if "gyro_stale" not in s.quality_reasons:
                    s.quality_reasons.append("gyro_stale")
            else:
                s.gyro_fresh = False
                s.error_flags.append("gyro_lost")
                if "gyro_lost" not in s.quality_reasons:
                    s.quality_reasons.append("gyro_lost")

        if not s.device_connected:
            s.error_flags.append("device_disconnected")
            if "device_disconnected" not in s.quality_reasons:
                s.quality_reasons.append("device_disconnected")

        if not s.stream_alive or not s.sensor_stream_active:
            s.error_flags.append("stream_inactive")
            if "stream_inactive" not in s.quality_reasons:
                s.quality_reasons.append("stream_inactive")

        s.display_data_available = s.device_connected and (s.attention_seen_once or s.gyro_seen_once)
        s.focus_seen_once = bool(s.focus_seen_once or s.gyro_seen_once)

        raw_training_data_valid = (
            s.device_connected
            and s.stream_alive
            and s.sensor_stream_active
            and s.attention_seen_once
            and s.attention is not None
            and s.attention_fresh
            and s.gyro_seen_once
            and s.gyro_fresh
            and not s.error_flags
        )

        frame_key = (s.attention_last_update_ms, s.gyro_last_update_ms)
        if raw_training_data_valid:
            if frame_key != self._last_valid_frame_key:
                self._valid_signal_frames += 1
                self._last_valid_frame_key = frame_key
        else:
            self._valid_signal_frames = 0
            self._last_valid_frame_key = None

        s.training_data_valid = (
            raw_training_data_valid
            and self._valid_signal_frames >= self._warmup_frames_required
        )

        s.quality = "ok"
        if s.error_flags:
            s.quality = "error"
        elif s.warning_flags:
            s.quality = "warning"

        s.control_data_valid = (
            s.training_data_valid
            and s.quality == "ok"
            and not s.warning_flags
            and not s.error_flags
        )

        s.fi_provisional = not bool(s.fi_valid)
        s.recovering = (
            s.device_connected
            and s.stream_alive
            and s.sensor_stream_active
            and not s.training_data_valid
        )

        if not s.device_connected or not s.stream_alive or not s.sensor_stream_active:
            s.control_state = "NO_SIGNAL"
            s.control_state_reason = "no_signal"
        elif s.attention is None:
            s.control_state = "RECOVERING"
            s.control_state_reason = "attention_missing"
        elif not s.training_data_valid:
            if s.attention < 30:
                s.control_state = "DISTRACTED"
                s.control_state_reason = "low_attention_warmup"
            elif s.attention < 45:
                s.control_state = "LOW_FOCUS"
                s.control_state_reason = "moderate_attention_warmup"
            else:
                s.control_state = "RECOVERING"
                s.control_state_reason = "warmup"
        elif s.attention < 30:
            s.control_state = "DISTRACTED"
            s.control_state_reason = "low_attention"
        elif s.attention < 45:
            s.control_state = "LOW_FOCUS"
            s.control_state_reason = "moderate_attention"
        else:
            s.control_state = "FOCUSED"
            s.control_state_reason = "attention_ok"

    def tick(self, now_ms: int, events: list[dict] | None = None) -> RealtimeSnapshot:
        """Compatibility API for legacy callers/tests."""
        if events is not None:
            self.ingest_events(events, now_ms=now_ms)
        else:
            self._snapshot.now_ms = now_ms
            self._refresh_derived_flags(now_ms)
        return self.get_snapshot()
