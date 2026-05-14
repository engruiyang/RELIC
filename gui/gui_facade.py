from __future__ import annotations

from copy import deepcopy
from typing import Any

from .gui_core_source import GuiCoreSnapshotSource


class GuiFacade:
    def __init__(self, mode: str = "mock", db_path: str = "data/relic_local.db") -> None:
        self.mode = mode
        self.db_path = db_path
        self.received_commands: list[dict[str, Any]] = []
        self.received_events: list[dict[str, Any]] = []
        self.last_command: dict[str, Any] = {}
        self.last_event: dict[str, Any] = {}
        self.last_command_result: dict[str, Any] = {}
        self.last_event_result: dict[str, Any] = {}
        self.command_count = 0
        self.event_count = 0

        self._core_source: GuiCoreSnapshotSource | None = None
        if self.mode == "core":
            self._core_source = GuiCoreSnapshotSource(db_path=self.db_path)
            return

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
            "source": "mock",
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
            "source": "mock",
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
            "source": "mock",
        }

    def get_app_state(self) -> dict[str, Any]:
        if self._core_source:
            return self._core_source.get_app_state()
        return deepcopy(self._app_state)

    def get_runtime_snapshot(self) -> dict[str, Any]:
        if self._core_source:
            return self._core_source.get_runtime_snapshot()
        return deepcopy(self._runtime_snapshot)

    def get_session_state(self) -> dict[str, Any]:
        if self._core_source:
            return self._core_source.get_session_state()
        return deepcopy(self._session_state)

    def handle_gui_command(self, command: str, args: dict[str, Any] | None = None) -> None:
        args = args or {}
        entry = {"command": command, "args": deepcopy(args)}
        self.received_commands.append(entry)
        self.last_command = deepcopy(entry)
        self.command_count = len(self.received_commands)
        print(f"[GUI COMMAND] command={command} args={args}", flush=True)
        if self._core_source:
            self.last_command_result = self._core_source.handle_command(command, args)
        else:
            self.last_command_result = {"status": "accepted", "reason": "mock_ok", "source": "mock"}

    def handle_gui_event(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        payload = payload or {}
        entry = {"event_type": event_type, "payload": deepcopy(payload)}
        self.received_events.append(entry)
        self.last_event = deepcopy(entry)
        self.event_count = len(self.received_events)
        print(f"[GUI EVENT] event_type={event_type} payload={payload}", flush=True)
        if self._core_source:
            self.last_event_result = self._core_source.handle_event(event_type, payload)
        else:
            self.last_event_result = {"status": "accepted", "reason": "mock_ok", "source": "mock"}
