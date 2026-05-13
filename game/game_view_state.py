from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
import json


@dataclass(slots=True)
class GameViewState:
    schema_version: str = "game_view.v1"
    session_id: str | None = None
    game_id: str | None = None
    view_type: str = "fake_status"
    updated_at_ms: int = 0
    score: float = 0.0
    combo: int = 0
    level: int = 1
    status: str = "stopped"
    control_state: str | None = None
    quality_state: str | None = None
    feedback_hint: str | None = None
    hud: dict[str, Any] = field(default_factory=dict)
    entities: list[dict[str, Any]] = field(default_factory=list)
    effects: list[dict[str, Any]] = field(default_factory=list)
    layout_hints: dict[str, Any] = field(default_factory=lambda: {"preferred_aspect": "16:9"})

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        json.dumps(data)
        return data
