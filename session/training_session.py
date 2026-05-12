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

    def set_status(self, status: str) -> None:
        if status not in ALLOWED_SESSION_STATUS:
            raise ValueError(f"invalid session status: {status}")
        self.status = status
