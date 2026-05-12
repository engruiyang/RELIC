from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
import json


@dataclass(slots=True)
class GameManifest:
    game_id: str
    display_name: str
    version: str
    supported_event_types: list[str] = field(default_factory=list)
    supported_command_types: list[str] = field(default_factory=list)
    min_duration_sec: int | None = None
    max_duration_sec: int | None = None
    requires_behavior_sample: bool = True
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        json.dumps(data)
        return data
