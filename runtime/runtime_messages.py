from __future__ import annotations


from dataclasses import asdict, dataclass, field, fields

from typing import Any, ClassVar, Mapping
import json


class RuntimeContractError(ValueError):
    """Raised when runtime contract validation fails."""



def _assert_json_serializable(data: Any) -> None:
    try:
        json.dumps(data)
    except TypeError as exc:
        raise RuntimeContractError(f"Data is not JSON serializable: {exc}") from exc



def _clip01(value: float | int | None) -> float | None:
    if value is None:
        return None
    return max(0.0, min(1.0, float(value)))


@dataclass(slots=True)
class RuntimeSnapshotView:
    schema_version: str = "1.0"
    session_id: str | None = None
    now_ms: int | None = None
    user_id: str | None = None
    game_id: str | None = None
    attention: float | None = None
    attention_age_ms: int | None = None
    attention_fresh: bool | None = None
    gyro_x: float | None = None
    gyro_y: float | None = None
    gyro_z: float | None = None
    gyro_age_ms: int | None = None
    gyro_fresh: bool | None = None
    sqi: float | None = None
    quality_state: str | None = None
    fi_raw: float | None = None
    fi_smoothed: float | None = None
    fi_valid: bool | None = None
    fi_confidence: float | None = None
    control_state: str | None = None
    control_state_reason: str | None = None
    warning_flags: list[str] | None = None
    error_flags: list[str] | None = None

    behavior_ready: bool | None = None
    interval_ms: int | None = None
    delta_ms: int | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "RuntimeSnapshotView":
        allowed = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in dict(data).items() if k in allowed})

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        _assert_json_serializable(data)
        return data


@dataclass(slots=True)
class RuntimeCommand:
    ALLOWED_TYPES: ClassVar[set[str]] = {
        "start_game",
        "pause_game",
        "resume_game",
        "stop_game",
        "set_difficulty",
        "set_feedback_mode",
    }

    schema_version: str = "1.0"
    command_id: str = ""
    session_id: str = ""
    game_id: str = ""
    command_type: str = ""
    issued_at_ms: int = 0
    payload: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.command_type not in self.ALLOWED_TYPES:
            raise RuntimeContractError(f"Unsupported command_type: {self.command_type}")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        _assert_json_serializable(data)
        return data


@dataclass(slots=True)
class GameEvent:
    ALLOWED_TYPES: ClassVar[set[str]] = {
        "score_update",
        "behavior_sample",
        "difficulty_request",
        "game_completed",
        "game_error",
        "user_action",
    }

    schema_version: str = "1.0"
    event_id: str = ""
    session_id: str = ""
    game_id: str = ""
    event_type: str = ""
    created_at_ms: int = 0
    payload: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.session_id:
            raise RuntimeContractError("GameEvent.session_id is required")
        if not self.game_id:
            raise RuntimeContractError("GameEvent.game_id is required")
        if self.event_type not in self.ALLOWED_TYPES:
            raise RuntimeContractError(f"Unsupported event_type: {self.event_type}")
        if self.event_type == "behavior_sample":
            self.payload = normalize_behavior_sample_payload(self.payload)
        _assert_json_serializable(self.payload)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        _assert_json_serializable(data)
        return data


def normalize_behavior_sample_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    for key in ("accuracy", "omission", "false_action", "rt_stability"):
        normalized[key] = _clip01(normalized.get(key))
    _assert_json_serializable(normalized)
    return normalized
