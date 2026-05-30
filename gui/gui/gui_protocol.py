from __future__ import annotations

from dataclasses import asdict, dataclass, field
from time import time
from typing import Any

GUI_PACKET_TYPES = {
    "app_state",
    "runtime_snapshot",
    "session_state",
    "gui_command",
    "gui_event",
}


@dataclass(slots=True)
class GuiPacket:
    type: str
    version: int
    seq: int
    timestamp_ms: int
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_payload(
        cls, packet_type: str, payload: dict[str, Any], seq: int = 0, version: int = 1
    ) -> "GuiPacket":
        return cls(
            type=packet_type,
            version=version,
            seq=seq,
            timestamp_ms=int(time() * 1000),
            payload=payload,
        )
