from __future__ import annotations

from dataclasses import asdict
from typing import Any

from data.data_center import DataCenter
from .gui_command_dispatcher import GuiCommandDispatcher
from .gui_mouse_input_router import GuiMouseInputRouter
from storage.sqlite_store import SqliteStore


class GuiCoreSnapshotSource:
    def __init__(self, db_path: str = "data/relic_local.db", source_mode: str = "core_readonly", duration_sec: int = 3, user_id: str = "demo_user", game_id: str = "fake_game", task6b_config: str = "config/task6b.yaml") -> None:
        self.db_path = db_path
        self.source_mode = source_mode
        self.duration_sec = duration_sec
        self.user_id = user_id
        self.game_id = game_id
        self.task6b_config = task6b_config
        self._store = SqliteStore(db_path=db_path)
        self._store.connect()
        self._data_center = DataCenter()
        self._current_user_id: str | None = None
        self._current_user_name = ""
        self._last_command_result: dict[str, Any] = {
            "status": "idle",
            "reason": "none",
            "source": "core_readonly",
        }
        self._last_event_result: dict[str, Any] = {
            "status": "idle",
            "reason": "none",
            "source": "core_readonly",
        }
        self.refresh_snapshot()
        self._dispatcher = GuiCommandDispatcher(self) if self.source_mode == "core_control" else None
        self._mouse_router = GuiMouseInputRouter(game_id=self.game_id) if self.source_mode == "core_control" else None

    def close(self) -> None:
        self._store.close()

    def refresh_snapshot(self) -> None:
        users = self._store.list_users()
        if users:
            current = users[0]
            self._current_user_id = str(current.get("user_id") or "")
            self._current_user_name = str(current.get("display_name") or "")
        else:
            self._current_user_id = "demo_user"
            self._current_user_name = "Demo User"

    def load_demo_user(self) -> None:
        self._current_user_id = "demo_user"
        self._current_user_name = "Demo User"

    def get_app_state(self) -> dict[str, Any]:
        last_session = self._get_last_session()
        calibration_status = "missing"
        if self._current_user_id:
            profile = self._store.get_user_profile(self._current_user_id)
            if profile and profile.get("last_calibration_id"):
                calibration_status = "available"
        return {
            "state": "READY",
            "current_user_id": self._current_user_id or "",
            "current_user_name": self._current_user_name,
            "device_connected": False,
            "calibration_status": calibration_status,
            "session_active": False,
            "current_game_id": str((last_session or {}).get("game_id") or "fake_game"),
            "warning_flags": ["readonly_mode"],
            "error_flags": ["device_disconnected"],
            "allowed_commands": ["refresh_snapshot", "load_demo_user"],
            "source": self.source_mode,
        }

    def get_runtime_snapshot(self) -> dict[str, Any]:
        snapshot = asdict(self._data_center.get_snapshot())
        return {
            "fi": float(snapshot.get("fi_smoothed") or 0.0),
            "sqi": float(snapshot.get("sqi") or 0.0),
            "attention": int(snapshot.get("attention") or 0),
            "attention_age_ms": snapshot.get("attention_age_ms"),
            "attention_fresh": bool(snapshot.get("attention_fresh")),
            "gyro_age_ms": snapshot.get("gyro_age_ms"),
            "gyro_fresh": bool(snapshot.get("gyro_fresh")),
            "control_state": str(snapshot.get("control_state") or "UNRELIABLE_SIGNAL"),
            "warning_flags": list(snapshot.get("warning_flags") or []),
            "error_flags": list(snapshot.get("error_flags") or []),
            "source": "core_no_live_stream",
        }

    def _get_last_session(self) -> dict[str, Any] | None:
        sessions = self._store.list_training_sessions(limit=1)
        return sessions[0] if sessions else None

    def handle_command(self, command: str, args: dict[str, Any]) -> dict[str, Any]:
        if self._dispatcher:
            result = self._dispatcher.dispatch(command, args).to_dict()
            self._last_command_result = dict(result)
            return dict(self._last_command_result)
        if command == "refresh_snapshot":
            self.refresh_snapshot()
            self._last_command_result = {"command": command, "accepted": True, "result": "accepted", "status": "accepted", "message": "refreshed", "reason": "refreshed", "source": "core_readonly", "payload": {}}
        elif command == "load_demo_user":
            self.load_demo_user()
            self._last_command_result = {"command": command, "accepted": True, "result": "accepted", "status": "accepted", "message": "demo_user_loaded", "reason": "demo_user_loaded", "source": "core_readonly", "payload": {}}
        elif command == "end_session":
            self._last_command_result = {"command": command, "accepted": True, "result": "noop", "status": "noop", "message": "no_active_session", "reason": "no_active_session", "source": "core_readonly", "payload": {}}
        else:
            self._last_command_result = {"command": command, "accepted": False, "result": "readonly_rejected", "status": "readonly_rejected", "message": "readonly_rejected", "reason": "readonly_rejected", "source": "core_readonly", "payload": {}}
        return dict(self._last_command_result)

    def handle_event(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.source_mode == "core_control" and self._mouse_router and event_type in {"target_click", "background_click"}:
            session_id = str(self.get_session_state().get("session_id") or "") or None
            self._last_event_result = self._mouse_router.route_gui_event(event_type=event_type, payload=payload, session_id=session_id)
        elif self.source_mode == "core_control":
            self._last_event_result = {"result": "recorded_only", "status": "accepted", "reason": "recorded_only", "source": "core_control", "event_type": event_type}
        else:
            self._last_event_result = {"result": "readonly_ignored", "status": "ignored", "reason": "readonly_ignored", "source": "core_readonly"}
        return dict(self._last_event_result)

    def apply_session_summary(self, summary: dict[str, Any]) -> None:
        self._latest_session = dict(summary)

    def get_session_state(self) -> dict[str, Any]:
        last_session = getattr(self, "_latest_session", None) or self._get_last_session() or {}
        return {
            "session_id": str(last_session.get("session_id") or ""),
            "user_id": str(last_session.get("user_id") or self._current_user_id or ""),
            "game_id": str(last_session.get("game_id") or ""),
            "session_active": False,
            "score": float(last_session.get("score") or 0.0),
            "warning_count": int(last_session.get("warning_count") or 0),
            "error_count": int(last_session.get("error_count") or 0),
            "log_path": str(last_session.get("log_path") or ""),
            "report_path": str(last_session.get("report_path") or ""),
            "platform_report_status": str(last_session.get("platform_report_status") or ""),
            "source": self.source_mode,
        }
