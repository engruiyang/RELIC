from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from runtime.runtime_messages import GameEvent, RuntimeSnapshotView
from session.training_session import TrainingSession
from storage.jsonl_logger import JsonlLogger
from storage.sqlite_store import SqliteStore


class SessionManager:
    def __init__(self, sqlite_store: SqliteStore, logs_dir: str = "logs/sessions", default_tick_ms: int = 1000):
        self._store = sqlite_store
        self._logs_dir = logs_dir
        self._default_tick_ms = default_tick_ms
        self._active_session: TrainingSession | None = None
        self._logger: JsonlLogger | None = None
        self._fi_sum = 0.0
        self._fi_count = 0
        self._sqi_sum = 0.0
        self._sqi_count = 0
        self._behavior_ready_ticks = 0

    def has_active_session(self) -> bool:
        return self._active_session is not None

    def get_active_session(self) -> TrainingSession | None:
        return self._active_session

    def start_session(self, user_id: str, game_id: str, calibration_id: str | None, task6b_config_path: str | None = None, task6b_config_snapshot: dict[str, Any] | None = None) -> tuple[bool, str, TrainingSession | None]:
        if self._active_session is not None:
            return False, "active_session_exists", None
        if not user_id:
            return False, "user_id_required", None
        if not game_id:
            return False, "game_id_required", None

        now = datetime.now(timezone.utc)
        session_id = f"session_{user_id}_{now.strftime('%Y%m%d_%H%M%S')}"
        log_path = str(Path(self._logs_dir) / f"{session_id}.jsonl")
        session = TrainingSession(
            session_id=session_id,
            user_id=user_id,
            game_id=game_id,
            calibration_id=calibration_id,
            started_at=now.isoformat(),
            log_path=log_path,
            estimator_version="task6b",
            task6b_config_path=task6b_config_path,
            task6b_config_snapshot=task6b_config_snapshot,
        )
        session.set_status("running")
        logger = JsonlLogger()
        logger.open(log_path)
        logger.write_event("session_start", session_id, {"user_id": user_id, "game_id": game_id, "calibration_id": calibration_id})
        if not calibration_id:
            logger.write_event("warning", session_id, {"reason": "calibration_id_missing"})

        self._active_session = session
        self._logger = logger
        self._fi_sum = self._sqi_sum = 0.0
        self._fi_count = self._sqi_count = 0
        self._behavior_ready_ticks = 0
        return True, "ok", session

    def record_runtime_snapshot(self, snapshot: RuntimeSnapshotView | dict[str, Any]) -> bool:
        if self._active_session is None or self._logger is None:
            return False
        view = snapshot if isinstance(snapshot, RuntimeSnapshotView) else RuntimeSnapshotView.from_dict(snapshot)
        payload = view.to_dict()
        self._logger.write_event("runtime_snapshot", self._active_session.session_id, payload)
        self._active_session.tick_count += 1
        tick_ms = int(payload.get("interval_ms") or payload.get("delta_ms") or self._default_tick_ms)
        q = payload.get("quality_state")
        if q == "ok" and payload.get("fi_valid") is True:
            self._active_session.valid_duration_ms += tick_ms
        if q == "warning":
            self._active_session.warning_duration_ms += tick_ms
        if payload.get("control_state") == "UNRELIABLE_SIGNAL" or q in {"invalid", "error"}:
            self._active_session.unreliable_duration_ms += tick_ms
        if payload.get("error_flags"):
            self._active_session.error_count += len(payload.get("error_flags") or [])
        if isinstance(payload.get("fi_smoothed"), (int, float)):
            self._fi_sum += float(payload["fi_smoothed"])
            self._fi_count += 1
            self._logger.write_event("focus_estimate", self._active_session.session_id, {"fi_smoothed": payload.get("fi_smoothed"), "fi_valid": payload.get("fi_valid")})
        if isinstance(payload.get("sqi"), (int, float)):
            self._sqi_sum += float(payload["sqi"])
            self._sqi_count += 1
        if payload.get("control_state"):
            c = self._active_session.control_state_summary
            c[payload["control_state"]] = c.get(payload["control_state"], 0) + 1
        if payload.get("behavior_ready") is True:
            self._behavior_ready_ticks += 1
        return True

    def record_game_event(self, game_event: GameEvent | dict[str, Any]) -> bool:
        if self._active_session is None or self._logger is None:
            return False
        event = game_event if isinstance(game_event, GameEvent) else GameEvent(**game_event)
        if event.session_id != self._active_session.session_id:
            self.record_warning("mismatched_game_event_session", {"event_session_id": event.session_id})
            return False
        if event.game_id != self._active_session.game_id:
            self.record_warning("mismatched_game_event_game", {"event_game_id": event.game_id})
            return False
        self._logger.write_event("game_event", self._active_session.session_id, event.to_dict())
        if event.event_type == "behavior_sample":
            self._active_session.has_behavior_samples = True
        if event.event_type == "score_update":
            self._active_session.score = float(event.payload.get("score", self._active_session.score or 0.0))
        return True

    def record_warning(self, reason: str, payload: dict[str, Any] | None = None) -> None:
        if self._active_session and self._logger:
            self._logger.write_event("warning", self._active_session.session_id, {"reason": reason, "payload": payload or {}})

    def record_error(self, reason: str, payload: dict[str, Any] | None = None) -> None:
        if self._active_session and self._logger:
            self._active_session.error_count += 1
            self._logger.write_event("error", self._active_session.session_id, {"reason": reason, "payload": payload or {}})

    def end_session(self, reason: str = "user_end") -> TrainingSession | None:
        return self._finalize("ended", reason)

    def abort_session(self, reason: str) -> TrainingSession | None:
        if self._active_session and self._logger:
            self._logger.write_event("error", self._active_session.session_id, {"reason": reason})
        return self._finalize("aborted", reason)

    def safe_shutdown(self) -> None:
        if self._active_session is not None:
            self.abort_session("safe_shutdown")

    def _finalize(self, status: str, reason: str) -> TrainingSession | None:
        if self._active_session is None or self._logger is None:
            return None
        now = datetime.now(timezone.utc).isoformat()
        s = self._active_session
        s.ended_at = now
        s.end_reason = reason
        s.set_status(status)
        if s.tick_count > 0:
            s.behavior_ready_ratio = self._behavior_ready_ticks / s.tick_count
        s.final_fi_avg = None if self._fi_count == 0 else self._fi_sum / self._fi_count
        s.final_sqi_avg = None if self._sqi_count == 0 else self._sqi_sum / self._sqi_count
        self._logger.write_event("session_end", s.session_id, {"status": s.status, "reason": reason})
        self._logger.close()
        self._store.upsert_training_session(self._to_summary_row(s))
        self._active_session = None
        self._logger = None
        return s

    def _to_summary_row(self, s: TrainingSession) -> dict[str, Any]:
        return {
            "session_id": s.session_id,
            "user_id": s.user_id,
            "game_id": s.game_id,
            "calibration_id": s.calibration_id,
            "started_at": s.started_at,
            "ended_at": s.ended_at,
            "status": s.status,
            "log_path": s.log_path,
            "valid_duration_ms": s.valid_duration_ms,
            "warning_duration_ms": s.warning_duration_ms,
            "unreliable_duration_ms": s.unreliable_duration_ms,
            "error_count": s.error_count,
            "final_fi_avg": s.final_fi_avg,
            "final_sqi_avg": s.final_sqi_avg,
            "control_state_summary": json.dumps(s.control_state_summary, ensure_ascii=False),
            "score": s.score,
            "end_reason": s.end_reason,
            "estimator_version": s.estimator_version,
            "task6b_config_path": s.task6b_config_path,
            "task6b_config_snapshot": json.dumps(s.task6b_config_snapshot or {}, ensure_ascii=False),
            "behavior_ready_ratio": s.behavior_ready_ratio,
            "has_behavior_samples": 1 if s.has_behavior_samples else 0,
        }
