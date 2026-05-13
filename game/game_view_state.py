from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping
import json


class GameViewStateValidationError(ValueError):
    pass


REQUIRED_FIELDS = {
    "schema_version", "session_id", "game_id", "view_type", "updated_at_ms", "status", "score", "combo", "level", "control_state", "quality_state", "feedback_hint", "hud", "entities", "effects", "layout_hints",
}


@dataclass(slots=True)
class GameViewState:
    schema_version: str = "game_view.v1"
    session_id: str = ""
    game_id: str = ""
    view_type: str = "fake_status"
    updated_at_ms: int = 0
    status: str = "idle"
    score: float = 0.0
    combo: int = 0
    level: int = 1
    control_state: str = "UNRELIABLE_SIGNAL"
    quality_state: str = "unknown"
    feedback_hint: str = "neutral"
    hud: dict[str, Any] = field(default_factory=dict)
    entities: list[dict[str, Any]] = field(default_factory=list)
    effects: list[dict[str, Any]] = field(default_factory=list)
    layout_hints: dict[str, Any] = field(default_factory=lambda: {"preferred_aspect": "16:9", "safe_area": [0.05, 0.05, 0.9, 0.9], "theme": "default"})

    def validate(self) -> None:
        data = asdict(self)
        if self.schema_version != "game_view.v1":
            raise GameViewStateValidationError("schema_version must be game_view.v1")
        if not self.session_id or not self.game_id:
            raise GameViewStateValidationError("session_id and game_id are required")
        if not isinstance(self.hud, dict) or not isinstance(self.layout_hints, dict):
            raise GameViewStateValidationError("hud/layout_hints must be dict")
        if not isinstance(self.entities, list) or not isinstance(self.effects, list):
            raise GameViewStateValidationError("entities/effects must be list")
        if not all(isinstance(x, dict) for x in self.entities):
            raise GameViewStateValidationError("entities must be list[dict]")
        if not all(isinstance(x, dict) for x in self.effects):
            raise GameViewStateValidationError("effects must be list[dict]")
        try:
            json.dumps(data)
        except TypeError as exc:
            raise GameViewStateValidationError(f"view state not JSON serializable: {exc}") from exc

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    def to_json_safe(self) -> dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "GameViewState":
        missing = REQUIRED_FIELDS - set(data.keys())
        if missing:
            raise GameViewStateValidationError(f"missing required fields: {sorted(missing)}")
        obj = cls(**{k: data[k] for k in REQUIRED_FIELDS})
        obj.validate()
        return obj
