from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol, runtime_checkable
import json


@dataclass(slots=True)
class GameInputEvent:
    event_id: str
    session_id: str
    game_id: str
    input_type: str
    created_at_ms: int
    source: str
    x_norm: float
    y_norm: float
    button: int
    raw_event_type: str
    debug_hit: bool | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class GameEvent:
    schema_version: str
    event_id: str
    session_id: str
    game_id: str
    event_type: str
    created_at_ms: int
    reportable: bool
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class BehaviorSample:
    window_ms: int
    target_count: int
    correct_count: int
    omission_count: int
    false_action_count: int
    action_count: int
    rt_samples_ms: list[int] = field(default_factory=list)
    accuracy: float = 0.0
    omission: float = 0.0
    false_action: float = 0.0
    rt_stability: float = 0.0
    game_specific: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class VisualEvent:
    event_id: str
    kind: str
    target_id: str
    x: float
    y: float
    effect_key: str
    style_key: str
    intensity: float
    duration_ms: int
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class GameEntity:
    id: str
    kind: str
    role: str
    x: float
    y: float
    radius: float
    state: str
    style_key: str
    asset_key: str
    interactive: bool
    hit_shape: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class GameViewState:
    game_id: str
    view_version: str
    frame_id: int
    score: int
    combo: int
    level: int
    hud: dict[str, Any] = field(default_factory=dict)
    entities: list[GameEntity] = field(default_factory=list)
    visual_events: list[VisualEvent] = field(default_factory=list)
    layout_hints: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        json.dumps(data)
        return data


@runtime_checkable
class GameClientPort(Protocol):
    @property
    def game_id(self) -> str: ...

    @property
    def manifest(self) -> dict[str, Any]: ...

    def start(self, context: dict[str, Any]) -> None: ...
    def stop(self, reason: str) -> None: ...
    def update(self, runtime_snapshot: dict[str, Any], dt_ms: int) -> None: ...
    def handle_input(self, game_input_event: GameInputEvent) -> None: ...
    def build_game_view(self) -> GameViewState: ...
    def collect_game_events(self) -> list[GameEvent]: ...
    def collect_behavior_sample(self) -> BehaviorSample: ...
    def is_completed(self) -> bool: ...
    def get_score(self) -> int: ...
