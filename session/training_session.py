from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

ALLOWED_SESSION_STATUS = {"created", "running", "ended", "aborted", "error"}


@dataclass(slots=True)
class TrainingSession:
    session_id: str
    user_id: str
    game_id: str
    calibration_id: str | None
    started_at: str
    ended_at: str | None = None
    status: str = "created"
    log_path: str = ""
    tick_count: int = 0
    valid_duration_ms: int = 0
    warning_duration_ms: int = 0
    unreliable_duration_ms: int = 0
    error_count: int = 0
    final_fi_avg: float | None = None
    final_sqi_avg: float | None = None
    control_state_summary: dict[str, int] = field(default_factory=dict)
    score: float | None = None
    end_reason: str | None = None
    estimator_version: str = "task6b"
    task6b_config_path: str | None = None
    task6b_config_snapshot: dict[str, Any] | None = None
    behavior_ready_ratio: float = 0.0
    has_behavior_samples: bool = False
    total_duration_ms: int = 0
    observed_tick_count: int = 0
    valid_tick_count: int = 0
    warning_tick_count: int = 0
    unreliable_tick_count: int = 0
    quality_state_summary: dict[str, int] = field(default_factory=dict)
    quality_state_duration_summary: dict[str, int] = field(default_factory=dict)
    control_state_duration_summary: dict[str, int] = field(default_factory=dict)
    fi_min: float | None = None
    fi_max: float | None = None
    fi_last: float | None = None
    sqi_min: float | None = None
    sqi_max: float | None = None
    sqi_last: float | None = None
    game_event_count: int = 0
    score_update_count: int = 0
    behavior_sample_count: int = 0
    user_action_count: int = 0
    game_error_count: int = 0
    score_last: float | None = None
    score_max: float | None = None
    score_total_delta: float = 0.0
    game_completed: bool = False
    game_completion_reason: str | None = None

    def set_status(self, status: str) -> None:
        if status not in ALLOWED_SESSION_STATUS:
            raise ValueError(f"invalid session status: {status}")
        self.status = status
