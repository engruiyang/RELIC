from dataclasses import dataclass
from typing import Any


@dataclass
class PlatformMessage:
    kind: str
    payload: dict


class PlatformMessageParser:
    """Convert platform/live payloads into Task2-compatible raw events."""

    def to_raw_events(self, payload: dict[str, Any], now_ms: int) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []

        connected = payload.get("connected")
        if connected is not None:
            events.append({"type": "device_status", "connected": bool(connected)})

        bridge_alive = payload.get("bridge_alive")
        if bridge_alive is not None:
            events.append({"type": "stream_status", "alive": bool(bridge_alive), "active": bool(bridge_alive)})

        attention = payload.get("attention_value")
        if attention is not None:
            events.append({"type": "attention", "value": int(attention), "timestamp_ms": now_ms})

        gx, gy, gz = payload.get("gyro_x"), payload.get("gyro_y"), payload.get("gyro_z")
        if gx is not None or gy is not None or gz is not None:
            events.append(
                {
                    "type": "gyroscope",
                    "x": gx,
                    "y": gy,
                    "z": gz,
                    "timestamp_ms": now_ms,
                }
            )

        return events
