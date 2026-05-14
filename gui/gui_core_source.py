from __future__ import annotations

from dataclasses import asdict
from typing import Any

from data.data_center import DataCenter
from storage.sqlite_store import SqliteStore


class GuiCoreSnapshotSource:
    def __init__(self, db_path: str = "data/relic_local.db") -> None:
        self.db_path = db_path
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
            "source": "core_readonly",
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

    def get_session_state(self) -> dict[str, Any]:
        last_session = self._get_last_session() or {}
        return {
            "session_id": str(last_session.get("session_id") or ""),
            "user_id": str(last_session.get("user_id") or self._current_user_id or ""),
            "game_id": str(last_session.get("game_id") or ""),
            "session_active": False,
            "score": float(last_session.get("score") or 0.0),
            "warning_count": 0,
            "error_count": int(last_session.get("error_count") or 0),
            "log_path": str(last_session.get("log_path") or ""),
            "report_path": "",
            "source": "core_readonly",
        }

    def _get_last_session(self) -> dict[str, Any] | None:
        sessions = self._store.list_training_sessions(limit=1)
        return sessions[0] if sessions else None

    def handle_command(self, command: str, args: dict[str, Any]) -> dict[str, Any]:
        if command == "refresh_snapshot":
            self.refresh_snapshot()
            self._last_command_result = {"result": "accepted", "status": "accepted", "reason": "refreshed", "source": "core_readonly"}
        elif command == "load_demo_user":
            self.load_demo_user()
            self._last_command_result = {"result": "accepted", "status": "accepted", "reason": "demo_user_loaded", "source": "core_readonly"}
        elif command == "end_session":
            self._last_command_result = {"result": "noop", "status": "noop", "reason": "no_active_session", "source": "core_readonly"}
        else:
            self._last_command_result = {"result": "readonly_rejected", "status": "rejected", "reason": "readonly_rejected", "source": "core_readonly"}
        return dict(self._last_command_result)

    def handle_event(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        _ = (event_type, payload)
        self._last_event_result = {"result": "readonly_ignored", "status": "ignored", "reason": "readonly_ignored", "source": "core_readonly"}
        return dict(self._last_event_result)
