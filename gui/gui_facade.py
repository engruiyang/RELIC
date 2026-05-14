from __future__ import annotations

from copy import deepcopy
from typing import Any


class GuiFacade:
    def __init__(self, mode: str = "mock") -> None:
        self.mode = mode
        self._app_state = {
            "state": "READY",
            "current_user_id": "demo_user",
            "current_user_name": "Demo User",
            "device_connected": True,
            "calibration_status": "passed",
            "session_active": False,
            "current_game_id": "fake_game",
            "warning_flags": [],
            "error_flags": [],
            "allowed_commands": [
                "load_demo_user",
                "start_mock_session",
                "end_session",
                "refresh_snapshot",
                "send_test_click",
            ],
        }
        self._runtime_snapshot = {
            "fi": 72.4,
            "sqi": 0.91,
            "attention": 63,
            "attention_age_ms": 420,
            "attention_fresh": True,
            "gyro_age_ms": 35,
            "gyro_fresh": True,
            "control_state": "STABLE_FOCUS",
            "warning_flags": [],
            "error_flags": [],
        }
        self._session_state = {
            "session_id": "mock_session",
            "user_id": "demo_user",
            "game_id": "fake_game",
            "session_active": False,
            "score": 31.0,
            "warning_count": 1,
            "error_count": 0,
            "log_path": "logs/sessions/mock_session.jsonl",
            "report_path": "reports/sessions/mock_session.md",
        }
        self.received_commands: list[dict[str, Any]] = []
        self.received_events: list[dict[str, Any]] = []

    def get_app_state(self) -> dict[str, Any]:
        return deepcopy(self._app_state)

    def get_runtime_snapshot(self) -> dict[str, Any]:
        return deepcopy(self._runtime_snapshot)

    def get_session_state(self) -> dict[str, Any]:
        return deepcopy(self._session_state)

    def handle_gui_command(self, command: str, args: dict[str, Any] | None = None) -> None:
        args = args or {}
        self.received_commands.append({"command": command, "args": deepcopy(args)})

    def handle_gui_event(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        payload = payload or {}
        self.received_events.append({"event_type": event_type, "payload": deepcopy(payload)})
