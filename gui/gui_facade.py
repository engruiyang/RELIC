from __future__ import annotations

from copy import deepcopy
from typing import Any

from .gui_core_source import GuiCoreSnapshotSource
from .gui_live_readonly_source import GuiLiveReadonlySource


class GuiFacade:
    def __init__(self, mode: str = "mock", db_path: str = "data/relic_local.db", duration_sec: int = 3, user_id: str = "demo_user", game_id: str = "fake_game", task6b_config: str = "config/task6b.yaml", host: str = "127.0.0.1", port: int = 8000) -> None:
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
        self.last_pointer_x: float | None = None
        self.last_pointer_y: float | None = None
        self.last_hit_state: bool | None = None
        self.last_game_event: dict[str, Any] = {}
        self.game_event_count = 0
        self.last_game_event_type = ""
        self.last_game_action_name = ""
        self.last_game_target_index: int | None = None
        self.last_game_view_summary: dict[str, Any] = {}
        self.last_game_view: dict[str, Any] = {}
        self.platform_message_count = 0
        self.last_platform_message: dict[str, Any] = {}
        self.last_platform_index: int | None = None
        self.last_platform_action = ""
        self.last_platform_result = ""

        self._core_source: GuiCoreSnapshotSource | None = None
        self._live_source: GuiLiveReadonlySource | None = None
        if self.mode in {"core", "core-control"}:
            source_mode = "core_control" if self.mode == "core-control" else "core_readonly"
            self._core_source = GuiCoreSnapshotSource(db_path=self.db_path, source_mode=source_mode, duration_sec=duration_sec, user_id=user_id, game_id=game_id, task6b_config=task6b_config)
            return
        if self.mode == "live-readonly":
            self._live_source = GuiLiveReadonlySource(host=host, port=port)
            self._live_source.start()
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
        if self._live_source:
            return self._live_source.get_app_state()
        if self._core_source:
            return self._core_source.get_app_state()
        return deepcopy(self._app_state)

    def get_runtime_snapshot(self) -> dict[str, Any]:
        if self._live_source:
            return self._live_source.get_runtime_snapshot()
        if self._core_source:
            return self._core_source.get_runtime_snapshot()
        return deepcopy(self._runtime_snapshot)

    def get_session_state(self) -> dict[str, Any]:
        if self._live_source:
            return self._live_source.get_session_state()
        if self._core_source:
            return self._core_source.get_session_state()
        return deepcopy(self._session_state)

    def get_game_view(self) -> dict[str, Any]:
        if self._core_source:
            return self._core_source.get_game_view()
        return {}

    def handle_gui_command(self, command: str, args: dict[str, Any] | None = None) -> None:
        args = args or {}
        entry = {"command": command, "args": deepcopy(args)}
        self.received_commands.append(entry)
        self.last_command = deepcopy(entry)
        self.command_count = len(self.received_commands)
        if self._core_source:
            self.last_command_result = self._core_source.handle_command(command, args)
        elif self._live_source:
            if command == "refresh_snapshot":
                self.last_command_result = {"command": command, "accepted": True, "status": "accepted", "message": "refreshed", "result": "accepted", "source": "live_readonly"}
            elif command == "load_demo_user":
                self.last_command_result = {"command": command, "accepted": True, "status": "noop", "message": "readonly_no_user", "result": "noop", "source": "live_readonly"}
            elif command == "start_mock_session":
                self.last_command_result = {"command": command, "accepted": False, "status": "readonly_rejected", "message": "readonly_rejected", "result": "readonly_rejected", "source": "live_readonly"}
            elif command == "end_session":
                self.last_command_result = {"command": command, "accepted": True, "status": "noop", "message": "no_active_session", "result": "noop", "source": "live_readonly"}
            else:
                self.last_command_result = {"command": command, "accepted": False, "status": "readonly_rejected", "message": "readonly_rejected", "result": "readonly_rejected", "source": "live_readonly"}
        else:
            self.last_command_result = {"command": command, "accepted": True, "status": "accepted", "message": "mock_ok", "payload": {}, "result": "accepted", "source": "mock"}
        print(f"[GUI COMMAND] command={command} args={args} result={self.last_command_result.get('accepted')} status={self.last_command_result.get('status')} message=\"{self.last_command_result.get('message', self.last_command_result.get('reason', ''))}\"", flush=True)

    def handle_gui_event(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        payload = payload or {}
        entry = {"event_type": event_type, "payload": deepcopy(payload)}
        self.received_events.append(entry)
        self.last_event = deepcopy(entry)
        self.event_count = len(self.received_events)
        if "x_norm" in payload:
            self.last_pointer_x = float(payload.get("x_norm"))
        if "y_norm" in payload:
            self.last_pointer_y = float(payload.get("y_norm"))
        if "hit" in payload:
            self.last_hit_state = bool(payload.get("hit"))
        if self._core_source:
            self.last_event_result = self._core_source.handle_event(event_type, payload)
        elif self._live_source:
            self.last_event_result = {"result": "readonly_ignored", "status": "ignored", "reason": "readonly_ignored", "source": "live_readonly"}
        else:
            self.last_event_result = {"result": "recorded", "status": "accepted", "reason": "mock_recorded", "source": "mock"}
        if self._core_source and self.mode == "core-control":
            self.last_game_event = deepcopy(self.last_event_result.get("last_game_event") or {})
            self.game_event_count = int(self.last_event_result.get("game_event_count") or self.game_event_count)
            self.last_game_view_summary = deepcopy(self.last_event_result.get("last_game_view_summary") or {})
            self.last_game_view = deepcopy(self.last_event_result.get("last_game_view") or {})
            self.last_game_event_type = str(self.last_game_event.get("event_type") or "")
            payload_data = self.last_game_event.get("payload") or {}
            self.last_game_action_name = str(payload_data.get("action_name") or "")
            target_idx = payload_data.get("target_index")
            self.last_game_target_index = int(target_idx) if isinstance(target_idx, int) else None
            self.platform_message_count = int(self.last_event_result.get("platform_message_count") or self.platform_message_count)
            self.last_platform_message = deepcopy(self.last_event_result.get("last_platform_message") or {})
            self.last_platform_index = self.last_platform_message.get("index") if isinstance(self.last_platform_message.get("index"), int) else None
            self.last_platform_action = str(self.last_platform_message.get("action_name") or "")
            self.last_platform_result = str(self.last_event_result.get("last_platform_result") or "")
        event_result = str(self.last_event_result.get("result") or self.last_event_result.get("reason") or "unknown")
        x_norm = payload.get("x_norm")
        y_norm = payload.get("y_norm")
        hit = payload.get("hit")
        print(f"[GUI EVENT] event_type={event_type} x={x_norm} y={y_norm} hit={hit} result={event_result}", flush=True)

    def close(self) -> None:
        if self._core_source:
            self._core_source.close()
        if self._live_source:
            self._live_source.stop()
