from __future__ import annotations

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
        self._logs_dir = Path(logs_dir)
        self._default_tick_ms = default_tick_ms
        self._active_session: TrainingSession | None = None
        self._logger: JsonlLogger | None = None
        self._fi_sum = 0.0
        self._fi_count = 0
        self._sqi_sum = 0.0
        self._sqi_count = 0
        self._behavior_ready_ticks = 0

    def has_active_session(self) -> bool: return self._active_session is not None
    def get_active_session(self) -> TrainingSession | None: return self._active_session

    def start_session(self, user_id: str, game_id: str, calibration_id: str | None, task6b_config_path: str | None = None, task6b_config_snapshot: dict[str, Any] | None = None) -> tuple[bool, str, TrainingSession | None]:
        if self._active_session is not None: return False, "active_session_exists", None
        if not user_id: return False, "user_id_required", None
        if not game_id: return False, "game_id_required", None
        now = datetime.now(timezone.utc)
        session_id = f"session_{user_id}_{now.strftime('%Y%m%d_%H%M%S')}"
        rel_log = Path("logs") / "sessions" / f"{session_id}.jsonl"
        abs_log = self._logs_dir / f"{session_id}.jsonl"
        session = TrainingSession(session_id=session_id, user_id=user_id, game_id=game_id, calibration_id=calibration_id, started_at=now.isoformat(), log_path=rel_log.as_posix(), estimator_version="task6b", task6b_config_path=task6b_config_path, task6b_config_snapshot=task6b_config_snapshot)
        session.set_status("running")
        self._logger = JsonlLogger(); self._logger.open(str(abs_log))
        self._logger.write_event("session_start", session_id, {"user_id": user_id, "game_id": game_id, "calibration_id": calibration_id, "log_path": session.log_path})
        if not calibration_id: self._logger.write_event("warning", session_id, {"reason": "calibration_id_missing"})
        self._active_session = session
        self._fi_sum = self._sqi_sum = 0.0; self._fi_count = self._sqi_count = 0; self._behavior_ready_ticks = 0
        return True, "ok", session

    def record_runtime_snapshot(self, snapshot: RuntimeSnapshotView | dict[str, Any]) -> bool:
        if not self._active_session or not self._logger: return False
        payload = (snapshot if isinstance(snapshot, RuntimeSnapshotView) else RuntimeSnapshotView.from_dict(snapshot)).to_dict()
        self._logger.write_event("runtime_snapshot", self._active_session.session_id, payload)
        s = self._active_session; s.tick_count += 1; s.observed_tick_count += 1
        tick_ms = int(payload.get("delta_ms") or payload.get("interval_ms") or self._default_tick_ms)
        s.total_duration_ms += tick_ms
        q = payload.get("quality_state")
        if q:
            s.quality_state_summary[q] = s.quality_state_summary.get(q, 0) + 1
            s.quality_state_duration_summary[q] = s.quality_state_duration_summary.get(q, 0) + tick_ms
        c = payload.get("control_state")
        if c:
            s.control_state_summary[c] = s.control_state_summary.get(c, 0) + 1
            s.control_state_duration_summary[c] = s.control_state_duration_summary.get(c, 0) + tick_ms
        if q == "ok" and payload.get("fi_valid") is True:
            s.valid_duration_ms += tick_ms; s.valid_tick_count += 1
        if q == "warning":
            s.warning_duration_ms += tick_ms; s.warning_tick_count += 1
        if c == "UNRELIABLE_SIGNAL" or q in {"invalid", "error"}:
            s.unreliable_duration_ms += tick_ms; s.unreliable_tick_count += 1
        if payload.get("error_flags"): s.error_count += len(payload.get("error_flags") or [])
        fi = payload.get("fi_smoothed")
        if isinstance(fi, (int, float)):
            fi = float(fi); self._fi_sum += fi; self._fi_count += 1; s.fi_last = fi
            s.fi_min = fi if s.fi_min is None else min(s.fi_min, fi); s.fi_max = fi if s.fi_max is None else max(s.fi_max, fi)
        sqi = payload.get("sqi")
        if isinstance(sqi, (int, float)):
            sqi = float(sqi); self._sqi_sum += sqi; self._sqi_count += 1; s.sqi_last = sqi
            s.sqi_min = sqi if s.sqi_min is None else min(s.sqi_min, sqi); s.sqi_max = sqi if s.sqi_max is None else max(s.sqi_max, sqi)
        if payload.get("behavior_ready") is True: self._behavior_ready_ticks += 1
        return True

    def record_game_event(self, game_event: GameEvent | dict[str, Any]) -> bool:
        if not self._active_session or not self._logger: return False
        event = game_event if isinstance(game_event, GameEvent) else GameEvent(**game_event)
        s = self._active_session
        if event.session_id != s.session_id:
            self.record_warning("mismatched_game_event_session", {"event_session_id": event.session_id}); return False
        if event.game_id != s.game_id:
            self.record_warning("mismatched_game_event_game", {"event_game_id": event.game_id}); return False
        self._logger.write_event("game_event", s.session_id, event.to_dict())
        s.game_event_count += 1
        if event.event_type == "score_update":
            s.score_update_count += 1
            score = event.payload.get("score")
            if isinstance(score, (int, float)):
                s.score_last = float(score); s.score = s.score_last
                s.score_max = s.score_last if s.score_max is None else max(s.score_max, s.score_last)
            delta = event.payload.get("score_delta")
            if isinstance(delta, (int, float)): s.score_total_delta += float(delta)
        elif event.event_type == "behavior_sample":
            s.behavior_sample_count += 1; s.has_behavior_samples = True
        elif event.event_type == "user_action":
            s.user_action_count += 1
        elif event.event_type == "game_error":
            s.game_error_count += 1; s.error_count += 1
        elif event.event_type == "game_completed":
            s.game_completed = True; s.game_completion_reason = event.payload.get("reason")
            fs = event.payload.get("final_score")
            if isinstance(fs, (int, float)): s.score_last = float(fs); s.score = s.score_last
        return True

    def record_warning(self, reason: str, payload: dict[str, Any] | None = None) -> None:
        if self._active_session and self._logger: self._logger.write_event("warning", self._active_session.session_id, {"reason": reason, "payload": payload or {}})

    def record_error(self, reason: str, payload: dict[str, Any] | None = None) -> None:
        if self._active_session and self._logger:
            self._active_session.error_count += 1
            self._logger.write_event("error", self._active_session.session_id, {"reason": reason, "payload": payload or {}})

    def end_session(self, reason: str = "user_end") -> TrainingSession | None: return self._finalize("ended", reason)
    def abort_session(self, reason: str) -> TrainingSession | None:
        if self._active_session and self._logger: self._logger.write_event("error", self._active_session.session_id, {"reason": reason})
        return self._finalize("aborted", reason)

    def _finalize(self, status: str, reason: str) -> TrainingSession | None:
        if not self._active_session or not self._logger: return None
        s = self._active_session
        s.ended_at = datetime.now(timezone.utc).isoformat(); s.end_reason = reason; s.set_status(status)
        s.behavior_ready_ratio = 0.0 if s.observed_tick_count == 0 else self._behavior_ready_ticks / s.observed_tick_count
        s.final_fi_avg = None if self._fi_count == 0 else self._fi_sum / self._fi_count
        s.final_sqi_avg = None if self._sqi_count == 0 else self._sqi_sum / self._sqi_count
        summary = self._to_summary_row(s)
        self._logger.write_event("session_summary", s.session_id, summary)
        self._logger.write_event("session_end", s.session_id, {"status": s.status, "reason": reason})
        self._logger.close(); self._store.upsert_training_session(summary)
        self._active_session = None; self._logger = None
        return s

    def _to_summary_row(self, s: TrainingSession) -> dict[str, Any]:
        return {k: v for k, v in {
            "session_id": s.session_id, "user_id": s.user_id, "game_id": s.game_id, "calibration_id": s.calibration_id,
            "started_at": s.started_at, "ended_at": s.ended_at, "status": s.status, "log_path": s.log_path,
            "valid_duration_ms": s.valid_duration_ms, "warning_duration_ms": s.warning_duration_ms, "unreliable_duration_ms": s.unreliable_duration_ms,
            "error_count": s.error_count, "final_fi_avg": s.final_fi_avg, "final_sqi_avg": s.final_sqi_avg,
            "control_state_summary": json.dumps(s.control_state_summary, ensure_ascii=False), "score": s.score, "end_reason": s.end_reason,
            "estimator_version": s.estimator_version, "task6b_config_path": s.task6b_config_path,
            "task6b_config_snapshot": json.dumps(s.task6b_config_snapshot or {}, ensure_ascii=False), "behavior_ready_ratio": s.behavior_ready_ratio,
            "has_behavior_samples": 1 if s.has_behavior_samples else 0, "total_duration_ms": s.total_duration_ms,
            "observed_tick_count": s.observed_tick_count, "valid_tick_count": s.valid_tick_count, "warning_tick_count": s.warning_tick_count,
            "unreliable_tick_count": s.unreliable_tick_count, "quality_state_summary": json.dumps(s.quality_state_summary, ensure_ascii=False),
            "quality_state_duration_summary": json.dumps(s.quality_state_duration_summary, ensure_ascii=False),
            "control_state_duration_summary": json.dumps(s.control_state_duration_summary, ensure_ascii=False), "fi_min": s.fi_min,
            "fi_max": s.fi_max, "fi_last": s.fi_last, "sqi_min": s.sqi_min, "sqi_max": s.sqi_max, "sqi_last": s.sqi_last,
            "game_event_count": s.game_event_count, "score_update_count": s.score_update_count, "behavior_sample_count": s.behavior_sample_count,
            "user_action_count": s.user_action_count, "game_error_count": s.game_error_count, "score_last": s.score_last,
            "score_max": s.score_max, "score_total_delta": s.score_total_delta, "game_completed": 1 if s.game_completed else 0,
            "game_completion_reason": s.game_completion_reason,
        }.items()}
