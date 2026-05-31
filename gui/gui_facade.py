from __future__ import annotations

from copy import deepcopy
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

from .gui_core_source import GuiCoreSnapshotSource
from .gui_live_readonly_source import GuiLiveReadonlySource
from .gui_live_control_source import GuiLiveControlSource
from core.resource_managers import build_render_resource_bundle
from storage.sqlite_store import SqliteStore
from .command_registry import build_page_command_manifest
from game.game_client_registry import create_game_client
from .desktop_model import (
    build_calibration_layout_render_resource,
    build_diagnostics_layout_render_resource,
    build_home_layout_render_resource,
    build_home_slots_render_resource,
    build_report_layout_render_resource,
    build_task26_fixed_card_render_resource,
    build_training_layout_render_resource,
    build_training_render_resource,
    build_training_slots_render_resource,
    build_user_layout_render_resource,
)


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

        self._render_resources = self._build_safe_render_resources(game_id=game_id)
        self._current_user_override = str(user_id or "")
        self._started_at_ms = int(time.time() * 1000)
        self._last_command_error = ""
        self._active_session_started_at_ms: int | None = None
        self._calibration_process: subprocess.Popen[str] | None = None
        self._calibration_output_lines: list[str] = []
        self._calibration_exit_code: int | None = None
        self._calibration_started_at_ms: int | None = None
        self._calibration_command: list[str] = []
        self._calibration_user_id = ""
        self._calibration_current_phase = ""
        self._last_report_detail: dict[str, Any] = {}
        self._last_report_list: list[dict[str, Any]] = []
        self._last_export_path = ""

        self._core_source: GuiCoreSnapshotSource | None = None
        self._live_source: GuiLiveReadonlySource | None = None
        self._live_control_source: GuiLiveControlSource | None = None
        if self.mode in {"core", "core-control"}:
            source_mode = "core_control" if self.mode == "core-control" else "core_readonly"
            self._core_source = GuiCoreSnapshotSource(db_path=self.db_path, source_mode=source_mode, duration_sec=duration_sec, user_id=user_id, game_id=game_id, task6b_config=task6b_config)
            return
        if self.mode == "live-readonly":
            self._live_source = GuiLiveReadonlySource(host=host, port=port)
            self._live_source.start()
            return
        if self.mode == "live-control":
            self._live_control_source = GuiLiveControlSource(host=host, port=port, user_id=user_id, game_id=game_id)
            self._live_control_source.start()
            return

        self._app_state = {
            "state": "READY",
            "current_user_id": user_id,
            "current_user_name": user_id,
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
                "select_trace_lock",
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
            "session_id": "",
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
        if self._live_control_source:
            return self._live_control_source.get_app_state()
        if self._live_source:
            return self._live_source.get_app_state()
        if self._core_source:
            return self._core_source.get_app_state()
        return deepcopy(self._app_state)

    def get_runtime_snapshot(self) -> dict[str, Any]:
        if self._live_control_source:
            return self._live_control_source.get_runtime_snapshot()
        if self._live_source:
            return self._live_source.get_runtime_snapshot()
        if self._core_source:
            return self._core_source.get_runtime_snapshot()
        return deepcopy(self._runtime_snapshot)

    def get_session_state(self) -> dict[str, Any]:
        if self._live_control_source:
            return self._live_control_source.get_session_state()
        if self._live_source:
            return self._live_source.get_session_state()
        if self._core_source:
            return self._core_source.get_session_state()
        return deepcopy(self._session_state)

    def get_game_view(self) -> dict[str, Any]:
        if self._live_control_source:
            return self._live_control_source.get_game_view()
        if self._core_source:
            return self._core_source.get_game_view()
        return {}

    def get_game_hud(self) -> dict[str, Any]:
        view = self.get_game_view() or {}
        hud = dict(view.get("hud") or {})
        hud.setdefault("game_id", view.get("game_id", self.get_app_state().get("current_game_id", "")))
        return hud

    def handle_gui_command(self, command: str, args: dict[str, Any] | None = None) -> None:
        args = args or {}
        entry = {"command": command, "args": deepcopy(args)}
        self.received_commands.append(entry)
        self.last_command = deepcopy(entry)
        self.command_count = len(self.received_commands)
        if self._core_source:
            self.last_command_result = self._core_source.handle_command(command, args)
        elif self._live_control_source:
            if command == "refresh_snapshot":
                self.last_command_result = {"command": command, "accepted": True, "status": "accepted", "message": "refreshed", "result": "accepted", "source": "live_control", "silent": bool(args.get("silent", False))}
            elif command == "load_demo_user":
                uid = str(args.get("user_id", "demo_user"))
                self._live_control_source.user_id = uid
                self.last_command_result = {"command": command, "accepted": True, "status": "accepted", "message": "user_loaded", "result": "accepted", "source": "live_control", "user_id": uid}
            elif command == "start_mock_session":
                self.last_command_result = self._live_control_source.start_live_debug_session(args.get("user_id"))
            elif command == "start_training_session":
                self.last_command_result = self._live_control_source.start_training_session(
                    args.get("user_id"),
                    args.get("db_path", self.db_path),
                    difficulty_mode=args.get("difficulty_mode"),
                    difficulty_level=args.get("difficulty_level", args.get("debug_difficulty", args.get("selected_difficulty_level"))),
                    game_duration_ms=args.get("game_duration_ms"),
                )
            elif command == "end_training_session":
                self.last_command_result = self._live_control_source.end_training_session()
            elif command == "end_session":
                self.last_command_result = self._live_control_source.end_training_session() if self._live_control_source.session_type == "training" else self._live_control_source.end_live_debug_session()
            elif command == "set_debug_difficulty":
                raw_mode = str(args.get("mode", args.get("difficulty_mode", ""))).strip().lower()
                raw_level = args.get("level", args.get("difficulty_level", args.get("debug_difficulty", args.get("selected_difficulty_level"))))
                if raw_mode == "auto":
                    raw_level = None
                elif raw_level is None and str(args.get("debug_difficulty", "")).strip().lower() in {"auto", "dynamic"}:
                    raw_level = None
                self.last_command_result = self._live_control_source.set_debug_difficulty(raw_level)
            elif command == "open_last_report":
                self.last_command_result = {"command": command, "accepted": True, "status": "noop", "message": "report_disabled_in_live_control", "result": "noop", "source": "live_control"}
            else:
                self.last_command_result = {"command": command, "accepted": False, "status": "rejected", "message": "unsupported_command", "result": "rejected", "source": "live_control"}
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
        if not bool(args.get("silent", False)):
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
        elif self._live_control_source:
            if event_type == "pointer_click":
                self.last_event_result = self._live_control_source.handle_pointer_click(payload)
            else:
                self.last_event_result = {"result": "ignored", "status": "ignored", "reason": "unsupported_event", "source": "live_control"}
        elif self._live_source:
            self.last_event_result = {"result": "readonly_ignored", "status": "ignored", "reason": "readonly_ignored", "source": "live_readonly"}
        else:
            self.last_event_result = {"result": "recorded", "status": "accepted", "reason": "mock_recorded", "source": "mock"}
        if self._live_control_source:
            self.last_game_event = deepcopy(self.last_event_result.get("last_game_event") or {})
            self.game_event_count = int(self.last_event_result.get("game_event_count") or self.game_event_count)
            self.last_game_view = deepcopy(self._live_control_source.get_game_view())
            self.last_game_view_summary = {"score": self.last_game_view.get("score",0), "combo": self.last_game_view.get("combo",0), "entity_count": len(self.last_game_view.get("entities") or []), "visual_event_count": len(self.last_game_view.get("visual_events") or [])}
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

    def _build_safe_render_resources(self, game_id: str) -> dict[str, Any]:
        try:
            return build_render_resource_bundle(game_id=game_id, theme_id="default", layout_id="minimal_gui")
        except Exception as exc:  # pragma: no cover
            return {
                "theme_id": "default",
                "layout_id": "minimal_gui",
                "game_id": game_id or "fake_game",
                "assets": {},
                "styles": {},
                "layout_regions": {},
                "missing_assets": [],
                "missing_styles": [],
                "missing_regions": [],
                "error": str(exc),
            }

    def _build_task26_home_slots_resource(self) -> dict[str, Any]:
        try:
            return build_home_slots_render_resource(Path("."))
        except Exception as exc:
            return {
                "task26_home_slots_payload": {},
                "task26_home_slots_status": "missing",
                "task26_home_slots_source": "assets/layouts/task26_examples/home_page.desktop_demo.json",
                "task26_home_slots_error": str(exc),
            }

    def _build_task26_home_layout_resource(self) -> dict[str, Any]:
        try:
            return build_home_layout_render_resource(Path("."))
        except Exception as exc:
            return {
                "task26_home_layout_payload": {},
                "task26_home_layout_status": "missing",
                "task26_home_layout_source": "assets/layouts/task26_examples/home_page.desktop_demo.json",
                "task26_home_layout_error": str(exc),
            }

    def _build_task26_training_layout_resource(self) -> dict[str, Any]:
        try:
            return build_training_layout_render_resource(Path("."))
        except Exception as exc:
            return {
                "task26_training_layout_payload": {},
                "task26_training_layout_status": "missing",
                "task26_training_layout_source": "assets/layouts/task26_examples/training_page.desktop_demo.json",
                "task26_training_layout_error": str(exc),
            }

    def _build_task26_user_layout_resource(self) -> dict[str, Any]:
        try:
            resource = build_user_layout_render_resource(Path("."))
            payload = resource.get("task26_user_layout_payload")
            if isinstance(payload, dict):
                self._hydrate_layout_payload_from_control_state(payload, self.get_control_state())
            return resource
        except Exception as exc:
            return {
                "task26_user_layout_payload": {},
                "task26_user_layout_status": "missing",
                "task26_user_layout_source": "assets/layouts/task26_examples/user_page.desktop_demo.json",
                "task26_user_layout_error": str(exc),
            }

    def _build_task26_calibration_layout_resource(self) -> dict[str, Any]:
        try:
            resource = build_calibration_layout_render_resource(Path("."))
            payload = resource.get("task26_calibration_layout_payload")
            if isinstance(payload, dict):
                self._hydrate_calibration_layout_payload(payload, self.get_control_state())
            return resource
        except Exception as exc:
            return {
                "task26_calibration_layout_payload": {},
                "task26_calibration_layout_status": "missing",
                "task26_calibration_layout_source": "assets/layouts/task26_examples/calibration_page.desktop_demo.json",
                "task26_calibration_layout_error": str(exc),
            }

    def _build_task26_report_layout_resource(self) -> dict[str, Any]:
        try:
            resource = build_report_layout_render_resource(Path("."))
            control_state = self.get_control_state()
            payload = resource.get("task26_report_layout_payload")
            if isinstance(payload, dict):
                self._hydrate_report_layout_payload(payload, control_state)
            report_context_keys = (
                "current_user_id",
                "latest_report_path",
                "report_selected_session_id",
                "report_selected_report_path",
                "report_selected_user_id",
                "report_available",
                "report_export_path",
                "report_preview",
                "report_selected_report_preview",
                "report_preview_available",
                "report_options_text",
                "report_list_text",
                "last_action_id",
                "last_action_status",
                "last_action_message",
            )
            resource["task26_report_context"] = {key: control_state.get(key, "n/a") for key in report_context_keys}
            resource["task26_report_context_status"] = "ok"
            resource["task26_report_context_source"] = "GuiFacade.get_control_state"
            return resource
        except Exception as exc:
            return {
                "task26_report_layout_payload": {},
                "task26_report_layout_status": "missing",
                "task26_report_layout_source": "assets/layouts/task26_examples/report_page.desktop_demo.json",
                "task26_report_layout_error": str(exc),
            }

    def _build_task26_diagnostics_layout_resource(self) -> dict[str, Any]:
        try:
            return build_diagnostics_layout_render_resource(Path("."))
        except Exception as exc:
            return {
                "task26_diagnostics_layout_payload": {},
                "task26_diagnostics_layout_status": "missing",
                "task26_diagnostics_layout_source": "assets/layouts/task26_examples/diagnostics_page.desktop_demo.json",
                "task26_diagnostics_layout_error": str(exc),
            }

    def _build_task26_training_resource(self) -> dict[str, Any]:
        try:
            return build_training_render_resource(Path("."))
        except Exception as exc:
            return {
                "task26_training_summary": {},
                "task26_training_status": "missing",
                "task26_training_source": "assets/layouts/task26_examples/training_page.desktop_demo.json",
                "task26_training_error": str(exc),
            }

    def _build_task26_training_slots_resource(self) -> dict[str, Any]:
        try:
            return build_training_slots_render_resource(Path("."))
        except Exception as exc:
            return {
                "task26_training_slots_payload": {},
                "task26_training_slots_status": "missing",
                "task26_training_slots_source": "assets/layouts/task26_examples/training_page.desktop_demo.json",
                "task26_training_slots_error": str(exc),
            }


    def _build_task26_fixed_card_resource(self) -> dict[str, Any]:
        try:
            return build_task26_fixed_card_render_resource(Path("."))
        except Exception as exc:
            return {
                "task26_fixed_card_registry": {},
                "task26_fixed_card_status": "missing",
                "task26_fixed_card_source": "assets/layouts/task26_examples/*.desktop_demo.json",
                "task26_fixed_card_error": str(exc),
            }


    def _build_task26_user_profile_context_resource(self) -> dict[str, Any]:
        try:
            state = self.get_control_state()
            keys = (
                "current_user_id",
                "profile_loaded",
                "last_calibration_id",
                "attention_low_threshold",
                "attention_high_threshold",
                "preferred_game_id",
                "difficulty_level",
                "attention_baseline",
                "calibration_usable",
                "gyro_noise_rms",
            )
            context = {key: state.get(key, "n/a") for key in keys}
            # Backward-compatible alias used by the formal Calibration page tests.
            # The canonical field remains calibration_progress_phase.
            if context.get("calibration_phase", "n/a") in (None, "", "n/a"):
                context["calibration_phase"] = context.get("calibration_progress_phase", "n/a")
            return {
                "task26_user_profile_context": context,
                "task26_user_profile_context_status": "ok",
                "task26_user_profile_context_source": "GuiFacade.get_control_state",
            }
        except Exception as exc:
            return {
                "task26_user_profile_context": {},
                "task26_user_profile_context_status": "missing",
                "task26_user_profile_context_error": str(exc),
            }

    def _build_task26_calibration_context_resource(self) -> dict[str, Any]:
        try:
            state = self.get_control_state()
            keys = (
                "current_user_id",
                "calibration_status",
                "calibration_usable",
                "latest_valid",
                "last_calibration_id",
                "calibration_id",
                "attention_baseline",
                "attention_std",
                "attention_low_threshold",
                "attention_high_threshold",
                "gyro_noise_rms",
                "failure_reason",
                "calibration_progress_status",
                "calibration_progress_running",
                "calibration_running",
                "calibration_progress_phase",
                "calibration_phase",
                "calibration_progress_exit_code",
                "calibration_progress_output_count",
                "calibration_progress_elapsed_sec",
                "calibration_progress_remaining_sec",
                "calibration_phase_remaining_sec",
                "calibration_total_remaining_sec",
                "calibration_progress_fraction",
                "calibration_progress_percent",
                "calibration_phase_prompt_text",
                "calibration_operator_guidance",
                "calibration_active_prompt_text",
                "calibration_phase_title",
                "calibration_phase_instruction",
                "calibration_phase_avoid_instruction",
                "calibration_phase_duration_hint",
            )
            context = {key: state.get(key, "n/a") for key in keys}
            return {
                "task26_calibration_context": context,
                "task26_calibration_context_status": "ok",
                "task26_calibration_context_source": "GuiFacade.get_control_state",
            }
        except Exception as exc:
            return {
                "task26_calibration_context": {},
                "task26_calibration_context_status": "missing",
                "task26_calibration_context_error": str(exc),
            }

    def get_render_resources(self) -> dict[str, Any]:
        resources = deepcopy(self._render_resources)
        resources.update(self._build_task26_home_slots_resource())
        resources.update(self._build_task26_home_layout_resource())
        resources.update(self._build_task26_training_resource())
        resources.update(self._build_task26_training_slots_resource())
        resources.update(self._build_task26_training_layout_resource())
        resources.update(self._build_task26_user_layout_resource())
        resources.update(self._build_task26_calibration_layout_resource())
        resources.update(self._build_task26_calibration_context_resource())
        resources.update(self._build_task26_report_layout_resource())
        resources.update(self._build_task26_diagnostics_layout_resource())
        resources.update(self._build_task26_user_profile_context_resource())
        resources.update(self._build_task26_fixed_card_resource())
        return resources


    def get_page_command_manifest(self) -> dict[str, Any]:
        return deepcopy(build_page_command_manifest())

    def close(self) -> None:
        if self._core_source:
            self._core_source.close()
        if self._live_source:
            self._live_source.stop()
        if self._live_control_source:
            self._live_control_source.stop()


    def _fetch_profile_summary(self, user_id: str) -> dict[str, Any]:
        store = SqliteStore(self.db_path)
        store.connect()
        try:
            user = store.get_user(user_id)
            if not user:
                return {"status": "user_not_found", "message": "user_not_found", "current_user_id": user_id}
            profile = store.get_user_profile(user_id)
            if not profile:
                return {"status": "profile_not_found", "message": "profile_not_found", "current_user_id": user_id, "user_type": user.get("user_type", "local_user"), "profile_loaded": False, "last_calibration_id": "n/a", "attention_low_threshold": "n/a", "attention_high_threshold": "n/a", "preferred_game_id": "n/a", "difficulty_level": "n/a"}
            low = profile.get("attention_low_threshold")
            high = profile.get("attention_high_threshold")
            difficulty = profile.get("difficulty_level")
            return {"status": "accepted", "message": "profile_loaded", "current_user_id": user_id, "user_type": user.get("user_type", "local_user"), "profile_loaded": True, "last_calibration_id": profile.get("last_calibration_id") or "n/a", "attention_low_threshold": 40 if low is None or low == "" else low, "attention_high_threshold": 70 if high is None or high == "" else high, "preferred_game_id": profile.get("preferred_game_id", "n/a"), "difficulty_level": 1 if difficulty is None or difficulty == "" else difficulty}
        finally:
            store.close()

    def _fetch_calibration_status(self, user_id: str) -> dict[str, Any]:
        user_id = str(user_id or "").strip()
        if not user_id:
            return {
                "status": "missing_user",
                "calibration_status": "missing_user",
                "last_calibration_id": "n/a",
                "calibration_usable": False,
                "latest_valid": False,
                "failure_reason": "missing_user",
                "source": "profile",
                "bound_calibration_user_matches": False,
                "binding_consistent": False,
            }

        store = SqliteStore(self.db_path)
        store.connect()
        try:
            profile = store.get_user_profile(user_id)
            if not profile:
                return {
                    "status": "profile_without_calibration",
                    "calibration_status": "profile_without_calibration",
                    "last_calibration_id": "n/a",
                    "calibration_usable": False,
                    "latest_valid": False,
                    "failure_reason": "profile_not_found",
                    "source": "profile",
                    "bound_calibration_user_matches": False,
                    "binding_consistent": False,
                }
            cal_id = str(profile.get("last_calibration_id") or "").strip()
            if not cal_id or cal_id == "n/a":
                return {
                    "status": "no_calibration",
                    "calibration_status": "no_calibration",
                    "last_calibration_id": "n/a",
                    "calibration_usable": False,
                    "latest_valid": False,
                    "failure_reason": "no_calibration",
                    "source": "profile",
                    "bound_calibration_user_matches": False,
                    "binding_consistent": True,
                }
            cp = store.get_calibration_profile(cal_id)
            if not cp:
                return {
                    "status": "no_calibration",
                    "calibration_status": "no_calibration",
                    "last_calibration_id": cal_id,
                    "calibration_usable": False,
                    "latest_valid": False,
                    "failure_reason": "calibration_id_not_found",
                    "source": "profile",
                    "bound_calibration_user_matches": False,
                    "binding_consistent": False,
                }

            cp_user_id = str(cp.get("user_id") or "").strip()
            if cp_user_id and cp_user_id != user_id:
                return {
                    "status": "binding_inconsistent",
                    "calibration_status": "binding_inconsistent",
                    "last_calibration_id": cal_id,
                    "calibration_usable": False,
                    "latest_valid": False,
                    "failure_reason": "calibration_user_mismatch",
                    "source": cp.get("calibration_type") or cp.get("source") or "calibration_profile",
                    "bound_calibration_user_matches": False,
                    "binding_consistent": False,
                    "calibration_user_id": cp_user_id,
                    "user_recovery_hint": "检测到历史绑定不一致。请为当前用户重新完成或重新绑定有效校准。",
                    "attention_baseline": "n/a",
                    "gyro_noise_rms": "n/a",
                }

            return {
                "status": "accepted",
                "calibration_status": "available",
                "last_calibration_id": cal_id,
                "calibration_usable": bool(cp.get("valid")),
                "latest_valid": bool(cp.get("valid")),
                "failure_reason": cp.get("failure_reason") or "",
                "source": cp.get("calibration_type") or cp.get("source") or "calibration_profile",
                "bound_calibration_user_matches": True,
                "binding_consistent": True,
                "calibration_user_id": cp_user_id or user_id,
                "attention_baseline": cp.get("attention_baseline") if cp.get("attention_baseline") is not None else "n/a",
                "gyro_noise_rms": cp.get("gyro_noise_rms") if cp.get("gyro_noise_rms") is not None else "n/a",
            }
        finally:
            store.close()

    def _connect_readonly_db(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _table_exists(self, conn: sqlite3.Connection, table_name: str) -> bool:
        row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)).fetchone()
        return row is not None

    def _table_columns(self, conn: sqlite3.Connection, table_name: str) -> set[str]:
        if not self._table_exists(conn, table_name):
            return set()
        return {str(row[1]) for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}

    def _calibration_table_name(self, conn: sqlite3.Connection) -> str | None:
        for table_name in ("calibration_profiles", "calibrations", "calibration_profile"):
            if self._table_exists(conn, table_name):
                return table_name
        return None

    def _normalize_calibration_record(self, row: dict[str, Any]) -> dict[str, Any]:
        item = dict(row)
        cal_id = item.get("calibration_id") or item.get("id") or item.get("profile_id") or ""
        item["calibration_id"] = str(cal_id)
        if "valid" in item:
            item["valid"] = bool(item.get("valid"))
        else:
            item["valid"] = False
        item.setdefault("calibration_type", item.get("type", "n/a") or "n/a")
        item.setdefault("source", item.get("source", item.get("calibration_type", "n/a")) or "n/a")
        item.setdefault("failure_reason", item.get("failure_reason", "") or "")
        item.setdefault("created_at", item.get("created_at", "n/a") or "n/a")
        for key in [
            "attention_baseline",
            "attention_std",
            "gyro_noise_rms",
            "gyro_stability_score",
            "signal_quality_baseline",
        ]:
            item.setdefault(key, "n/a")
        return item

    def _fetch_calibration_detail(self, calibration_id: str) -> dict[str, Any]:
        calibration_id = str(calibration_id or "").strip()
        if not calibration_id:
            return {"status": "missing_input", "message": "missing_calibration_id"}
        store = SqliteStore(self.db_path)
        store.connect()
        try:
            getter = getattr(store, "get_calibration_profile", None)
            if callable(getter):
                record = getter(calibration_id)
                if record:
                    detail = self._normalize_calibration_record(dict(record))
                    detail["status"] = "accepted"
                    detail["message"] = "calibration_loaded"
                    return detail
        finally:
            store.close()
        conn = self._connect_readonly_db()
        try:
            table_name = self._calibration_table_name(conn)
            if not table_name:
                return {"status": "no_calibration_table", "message": "no_calibration_table", "calibration_id": calibration_id}
            columns = self._table_columns(conn, table_name)
            id_col = "calibration_id" if "calibration_id" in columns else ("id" if "id" in columns else "profile_id")
            row = conn.execute(f"SELECT * FROM {table_name} WHERE {id_col}=?", (calibration_id,)).fetchone()
            if not row:
                return {"status": "calibration_not_found", "message": "calibration_not_found", "calibration_id": calibration_id}
            detail = self._normalize_calibration_record(dict(row))
            detail["status"] = "accepted"
            detail["message"] = "calibration_loaded"
            return detail
        finally:
            conn.close()

    def _fetch_calibration_list(self, user_id: str) -> dict[str, Any]:
        user_id = str(user_id or "").strip()
        if not user_id:
            return {"status": "missing_user", "message": "missing_user", "items": [], "items_count": 0, "calibrations": []}
        conn = self._connect_readonly_db()
        try:
            table_name = self._calibration_table_name(conn)
            if not table_name:
                return {"status": "accepted", "message": "no_calibration_table", "user_id": user_id, "items": [], "items_count": 0, "calibration_count": 0, "calibrations": []}
            columns = self._table_columns(conn, table_name)
            order_sql = " ORDER BY created_at DESC" if "created_at" in columns else " ORDER BY rowid DESC"
            if "user_id" in columns:
                rows = conn.execute(f"SELECT * FROM {table_name} WHERE user_id=?" + order_sql, (user_id,)).fetchall()
            else:
                rows = conn.execute(f"SELECT * FROM {table_name}" + order_sql).fetchall()

            items = [self._normalize_calibration_record(dict(row)) for row in rows]
            # Hard safety boundary: the calibration page is scoped by the current
            # User page selection. Never fall back to profile.last_calibration_id
            # here, because a polluted profile binding can point to another user's
            # calibration and poison the selector/bind path.
            items = [
                item for item in items
                if str(item.get("user_id") or "").strip() == user_id
            ]

            return {
                "status": "accepted",
                "message": "calibration_list",
                "user_id": user_id,
                "calibration_count": len(items),
                "items_count": len(items),
                "calibrations": items,
                "items": items,
            }
        finally:
            conn.close()

    def _fetch_latest_calibration(self, user_id: str) -> dict[str, Any]:
        listing = self._fetch_calibration_list(user_id)
        items = listing.get("items") or []
        if not items:
            return {"status": "no_calibration", "message": "no_calibration", "user_id": user_id}
        latest = dict(items[0])
        latest.setdefault("status", "accepted")
        latest.setdefault("message", "latest_calibration")
        return latest

    def _bind_calibration_summary(self, user_id: str, calibration_id: str) -> dict[str, Any]:
        user_id = str(user_id or "").strip()
        calibration_id = str(calibration_id or "").strip()
        if not user_id:
            return {"status": "missing_user", "message": "missing_user"}
        if not calibration_id:
            return {"status": "missing_input", "message": "missing_calibration_id", "user_id": user_id}
        detail = self._fetch_calibration_detail(calibration_id)
        if detail.get("status") != "accepted":
            return {"status": detail.get("status", "calibration_not_found"), "message": detail.get("message", "calibration_not_found"), "user_id": user_id, "calibration_id": calibration_id}
        detail_user_id = str(detail.get("user_id") or "").strip()
        if detail_user_id and detail_user_id != user_id:
            return {
                "status": "calibration_user_mismatch",
                "message": "calibration_user_mismatch",
                "user_id": user_id,
                "calibration_id": calibration_id,
                "calibration_user_id": detail_user_id,
                "accepted": False,
                "detail": detail,
            }
        if not bool(detail.get("valid")):
            return {"status": "invalid_calibration", "message": "invalid_calibration", "user_id": user_id, "calibration_id": calibration_id, "detail": detail}
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            if not self._table_exists(conn, "user_profiles"):
                return {"status": "profile_not_found", "message": "profile_not_found", "user_id": user_id, "calibration_id": calibration_id}
            columns = self._table_columns(conn, "user_profiles")
            if "last_calibration_id" not in columns or "user_id" not in columns:
                return {"status": "profile_schema_unsupported", "message": "profile_schema_unsupported", "user_id": user_id, "calibration_id": calibration_id}
            old_row = conn.execute("SELECT last_calibration_id FROM user_profiles WHERE user_id=?", (user_id,)).fetchone()
            if not old_row:
                return {"status": "profile_not_found", "message": "profile_not_found", "user_id": user_id, "calibration_id": calibration_id}
            old_id = old_row["last_calibration_id"]
            conn.execute("UPDATE user_profiles SET last_calibration_id=? WHERE user_id=?", (calibration_id, user_id))
            conn.commit()
            status = self._fetch_calibration_status(user_id)
            return {
                "status": "accepted",
                "message": "calibration_bound",
                "user_id": user_id,
                "calibration_id": calibration_id,
                "old_last_calibration_id": old_id or "n/a",
                "new_last_calibration_id": calibration_id,
                "calibration": status,
                "detail": detail,
            }
        finally:
            conn.close()

    def _cancel_calibration_summary(self, user_id: str) -> dict[str, Any]:
        if not user_id:
            return {"status": "missing_user", "message": "missing_user"}
        if self._calibration_process is not None and self._calibration_process.poll() is None:
            try:
                self._calibration_process.terminate()
            except Exception:
                pass
        self._calibration_process = None
        self._calibration_started_at_ms = None
        self._calibration_exit_code = None
        self._calibration_current_phase = ""
        self._calibration_user_id = user_id
        self._calibration_output_lines = ["[gui] Calibration guidance cancelled by user."]
        return {
            "status": "cancelled",
            "message": "cancelled_by_user",
            "user_id": user_id,
            "valid": False,
            "failure_reason": "cancelled_by_user",
            "progress": self._calibration_progress_summary(),
        }


    def _calibration_phase_durations_ms(self) -> list[int]:
        # Keep the durations aligned with the original no-head calibration prompts.
        # Phase 3 is intentionally allowed to use the upper bound from "8 to 12 seconds".
        return [2000, 3000, 12000, 1000]

    def _initial_calibration_progress_detail(self) -> dict[str, Any]:
        return {
            "phase": "n/a",
            "title": "等待校准",
            "user_instruction": "点击 Start Calibration 开始校准提示。",
            "avoid_instruction": "校准开始前请确认头环连接与佩戴状态。",
            "duration_hint": "n/a",
        }

    def _calibration_phase_prompts(self) -> list[dict[str, Any]]:
        return [
            {
                "phase": "phase 1/4",
                "title": "佩戴检查",
                "user_instruction": "请确认头环贴合额头，头部坐正，眼睛自然看向屏幕。",
                "avoid_instruction": "避免头发夹在电极和皮肤之间，不要移动头环。",
                "duration_hint": "约 2 秒",
            },
            {
                "phase": "phase 2/4",
                "title": "静止姿态校准",
                "user_instruction": "请保持头部静止，眼睛自然平视屏幕中央。",
                "avoid_instruction": "不要转头、低头、抬头或晃动身体。",
                "duration_hint": "约 3 秒",
            },
            {
                "phase": "phase 3/4",
                "title": "注意力基线检查",
                "user_instruction": "请自然平视屏幕中央，保持清醒和安静。",
                "avoid_instruction": "不要说话、不要刻意用力集中、不要大幅移动头部。",
                "duration_hint": "约 8 到 12 秒",
            },
            {
                "phase": "phase 4/4",
                "title": "结果计算",
                "user_instruction": "正在生成校准结果，请稍候。",
                "avoid_instruction": "无需操作。",
                "duration_hint": "约 1 秒",
            },
        ]

    def _format_calibration_phase_prompts(self) -> str:
        lines: list[str] = []
        for item in self._calibration_phase_prompts():
            lines.append(f"[{item.get('phase', '')}] {item.get('title', '')}".strip())
            user_instruction = str(item.get("user_instruction") or "").strip()
            avoid_instruction = str(item.get("avoid_instruction") or "").strip()
            duration_hint = str(item.get("duration_hint") or "").strip()
            if user_instruction:
                lines.append(f"  {user_instruction}")
            if avoid_instruction:
                lines.append(f"  {avoid_instruction}")
            if duration_hint:
                lines.append(f"  {duration_hint}")
        return "\n".join(lines)

    def _current_calibration_phase_detail(self) -> dict[str, Any]:
        current = self._calibration_current_phase or ""
        for item in self._calibration_phase_prompts():
            phase = str(item.get("phase") or "")
            title = str(item.get("title") or "")
            if current and (current in phase or phase in current or title in current):
                return dict(item)
        return {}

    def _calibration_progress_summary(self) -> dict[str, Any]:
        process = self._calibration_process
        if process is not None:
            polled = process.poll()
            if polled is not None:
                self._calibration_exit_code = int(polled)
                self._calibration_process = None
                self._calibration_started_at_ms = None
                self._calibration_current_phase = ""
                self._calibration_output_lines.append(
                    "[gui] Calibration process completed." if self._calibration_exit_code == 0 else f"[gui] Calibration process exited: {self._calibration_exit_code}"
                )
                if len(self._calibration_output_lines) > 300:
                    self._calibration_output_lines = self._calibration_output_lines[-300:]

        process_running = self._calibration_process is not None and self._calibration_process.poll() is None
        guidance_active = self._calibration_process is None and self._calibration_started_at_ms is not None and self._calibration_exit_code is None

        prompts = self._calibration_phase_prompts()
        durations_ms = self._calibration_phase_durations_ms()
        total_ms = sum(durations_ms) if durations_ms else 0
        elapsed_ms = 0
        if self._calibration_started_at_ms is not None:
            elapsed_ms = max(0, int(time.time() * 1000) - int(self._calibration_started_at_ms))

        output_tail = self._calibration_output_lines[-120:]
        phase_lines = [line for line in output_tail if line.startswith("[phase")]
        if phase_lines:
            self._calibration_current_phase = phase_lines[-1].split("]", 1)[0].strip("[") if "]" in phase_lines[-1] else phase_lines[-1]

        # Desktop/core guidance is a finite state machine: it advances through the
        # original four prompt phases once, then returns to idle. It must never loop.
        # Live-control/process mode uses the same phase clock for visible countdown;
        # the real subprocess remains the authority for actual completion.
        if guidance_active and total_ms > 0 and elapsed_ms >= total_ms:
            self._calibration_started_at_ms = None
            self._calibration_exit_code = None
            self._calibration_current_phase = ""
            self._calibration_process = None
            guidance_active = False
            elapsed_ms = 0

        running = bool(process_running or guidance_active)
        if process_running:
            status = "running"
        elif guidance_active:
            status = "guidance_running"
        else:
            status = "idle"

        current_phase_detail: dict[str, Any] = {}
        phase_elapsed_ms = 0
        phase_duration_ms = 0
        phase_remaining_ms = 0
        remaining_ms = 0
        progress_fraction = 0.0

        if running and prompts and total_ms > 0:
            # Use a clamped finite cursor for both real subprocess and GUI guidance.
            # This keeps the UI countdown meaningful when a real headset is connected,
            # while avoiding the old modulo-loop behavior.
            cursor = min(max(0, elapsed_ms), max(0, total_ms - 1))
            remaining_ms = max(0, total_ms - elapsed_ms)
            progress_fraction = min(1.0, max(0.0, elapsed_ms / float(total_ms)))
            acc = 0
            idx = len(prompts) - 1
            for i, duration in enumerate(durations_ms):
                if cursor < acc + duration:
                    idx = i
                    phase_elapsed_ms = max(0, cursor - acc)
                    phase_duration_ms = duration
                    phase_remaining_ms = max(0, duration - phase_elapsed_ms)
                    break
                acc += duration
            idx = min(idx, len(prompts) - 1)
            if phase_duration_ms == 0 and durations_ms:
                phase_duration_ms = durations_ms[idx]
                phase_elapsed_ms = min(phase_duration_ms, max(0, cursor - sum(durations_ms[:idx])))
                phase_remaining_ms = max(0, phase_duration_ms - phase_elapsed_ms)
            current_phase_detail = dict(prompts[idx])
            self._calibration_current_phase = str(current_phase_detail.get("phase") or f"phase {idx + 1}/{len(prompts)}")
        else:
            current_phase_detail = self._initial_calibration_progress_detail()
            self._calibration_current_phase = ""

        current_phase = str(current_phase_detail.get("phase") or (self._calibration_current_phase if running else "n/a") or "n/a")
        title = str(current_phase_detail.get("title") or "等待校准")
        user_instruction = str(current_phase_detail.get("user_instruction") or "点击 Start Calibration 开始校准提示。")
        avoid_instruction = str(current_phase_detail.get("avoid_instruction") or "校准开始前请确认头环连接与佩戴状态。")
        duration_hint = str(current_phase_detail.get("duration_hint") or "n/a")
        remaining_sec = round(phase_remaining_ms / 1000.0, 1) if running else 0.0
        total_remaining_sec = round(remaining_ms / 1000.0, 1) if running else 0.0
        elapsed_sec = round(elapsed_ms / 1000.0, 1) if running else 0.0

        if running:
            active_prompt_text = (
                f"[{current_phase}] {title}\n"
                f"{user_instruction}\n"
                f"{avoid_instruction}\n"
                f"本阶段剩余约 {remaining_sec:.1f} 秒；总剩余约 {total_remaining_sec:.1f} 秒。\n"
                f"{duration_hint}"
            )
        else:
            active_prompt_text = "[idle] 等待校准\n点击 Start Calibration 开始校准提示。\n校准结束或取消后会回到此状态。"

        phase_prompt_text = self._format_calibration_phase_prompts()
        output_text = "\n".join(output_tail) if running and output_tail else active_prompt_text

        return {
            "status": status,
            "running": running,
            "guidance_running": bool(guidance_active),
            "process_running": bool(process_running),
            "user_id": self._calibration_user_id,
            "started_at_ms": self._calibration_started_at_ms,
            "elapsed_ms": elapsed_ms if running else 0,
            "elapsed_sec": elapsed_sec,
            "remaining_ms": phase_remaining_ms if running else 0,
            "remaining_sec": remaining_sec,
            "total_remaining_ms": remaining_ms if running else 0,
            "total_remaining_sec": total_remaining_sec,
            "phase_elapsed_ms": phase_elapsed_ms if running else 0,
            "phase_duration_ms": phase_duration_ms if running else 0,
            "progress_fraction": round(progress_fraction, 3) if running else 0.0,
            "progress_percent": round(progress_fraction * 100.0, 1) if running else 0.0,
            "exit_code": self._calibration_exit_code,
            "current_phase": current_phase,
            "current_phase_detail": current_phase_detail,
            "phase_prompts": prompts,
            "phase_prompt_text": phase_prompt_text,
            "active_prompt_text": active_prompt_text,
            "output_count": len(self._calibration_output_lines),
            "output_tail": output_tail,
            "output_text": output_text,
            "operator_guidance": active_prompt_text,
            "command": " ".join(self._calibration_command) if self._calibration_command else "n/a",
        }

    def _calibration_output_reader(self, process: subprocess.Popen[str]) -> None:
        assert process.stdout is not None
        for line in process.stdout:
            cleaned = line.rstrip()
            if cleaned:
                self._calibration_output_lines.append(cleaned)
                if cleaned.startswith("[phase"):
                    self._calibration_current_phase = cleaned.split("]", 1)[0].strip("[") if "]" in cleaned else cleaned
                if len(self._calibration_output_lines) > 300:
                    self._calibration_output_lines = self._calibration_output_lines[-300:]
        process.wait()
        self._calibration_exit_code = int(process.returncode or 0)

    def _start_calibration_summary(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not user_id:
            return {
                "status": "missing_user",
                "message": "missing_user",
                "progress": self._calibration_progress_summary(),
            }

        self._set_current_user_context(user_id)
        calibration_type = str(payload.get("calibration_type") or "auto").strip() or "auto"
        if calibration_type == "auto":
            profile = self._fetch_profile_summary(user_id)
            status = self._fetch_calibration_status(user_id)
            last_calibration_id = str(status.get("last_calibration_id") or profile.get("last_calibration_id") or "").strip()
            profile_loaded = bool(profile.get("profile_loaded", False))
            has_usable_bound_calibration = (
                profile_loaded
                and status.get("status") == "accepted"
                and bool(status.get("calibration_usable", False))
                and last_calibration_id
                and last_calibration_id != "n/a"
            )
            calibration_type = "quick_check" if has_usable_bound_calibration else "first_profile"
        source = str(payload.get("source") or ("ipc if self.mode == live-control else mock")).strip()
        if source == "ipc if self.mode == live-control else mock":
            source = "ipc" if self.mode == "live-control" else "mock"

        # In mock/read-only tests, do not spawn the real CLI. Return the same phase prompts so
        # the GUI can show a deterministic progress/confirmation panel.
        if self.mode == "mock":
            self._calibration_user_id = user_id
            self._calibration_started_at_ms = int(time.time() * 1000)
            self._calibration_exit_code = 0
            self._calibration_current_phase = "phase guide"
            self._calibration_output_lines = ["[calibration] mock start guidance"] + self._format_calibration_phase_prompts().splitlines() + ["mock_gui_progress_completed"]
            return {
                "status": "start_guidance",
                "message": "calibration_progress_guidance_ready",
                "progress": self._calibration_progress_summary(),
            }

        if self._calibration_process is not None and self._calibration_process.poll() is None:
            return {
                "status": "already_running",
                "message": "calibration_already_running",
                "progress": self._calibration_progress_summary(),
            }

        cmd = [
            sys.executable,
            "-m",
            "ui_cli.run_calibration_debug",
            "--action",
            "start",
            "--mode",
            "user",
            "--user-id",
            user_id,
            "--db-path",
            self.db_path,
            "--calibration-type",
            calibration_type,
            "--source",
            source,
        ]
        host = str(payload.get("host") or "").strip()
        port = str(payload.get("port") or "").strip()
        if host:
            cmd.extend(["--host", host])
        if port:
            cmd.extend(["--port", port])

        self._calibration_command = cmd
        self._calibration_user_id = user_id
        self._calibration_output_lines = [
            "[gui] Calibration start requested.",
            "[gui] Waiting for CLI phase prompts...",
        ] + self._format_calibration_phase_prompts().splitlines()
        self._calibration_exit_code = None
        self._calibration_started_at_ms = int(time.time() * 1000)
        self._calibration_current_phase = "phase 1/4"
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
        except Exception as exc:
            self._calibration_process = None
            self._calibration_exit_code = -1
            self._calibration_output_lines.append(f"[gui] failed_to_start: {exc}")
            return {
                "status": "start_failed",
                "message": "failed_to_start_calibration",
                "progress": self._calibration_progress_summary(),
            }

        self._calibration_process = process
        threading.Thread(target=self._calibration_output_reader, args=(process,), daemon=True).start()
        return {
            "status": "started",
            "message": "calibration_process_started",
            "progress": self._calibration_progress_summary(),
        }


    def _session_table_name(self, conn: sqlite3.Connection) -> str | None:
        for table_name in (
            "session_summaries",
            "training_sessions",
            "sessions",
            "session_summary",
            "session_records",
        ):
            if self._table_exists(conn, table_name):
                return table_name
        return None

    def _normalize_session_record(self, row: dict[str, Any]) -> dict[str, Any]:
        item = dict(row)
        session_id = item.get("session_id") or item.get("id") or item.get("session_uuid") or ""
        item["session_id"] = str(session_id)
        item.setdefault("user_id", item.get("current_user_id", item.get("owner_user_id", "")) or "")
        item.setdefault("game_id", item.get("game", item.get("current_game_id", "")) or "")
        item.setdefault("status", item.get("training_status", item.get("state", "")) or "")
        item.setdefault("score", item.get("score_last", item.get("score", item.get("score_total", "n/a"))) or "n/a")
        item.setdefault("report_path", item.get("latest_report_path", item.get("report_file", "")) or "")
        item["report_path"] = self._infer_existing_report_path(str(item.get("session_id") or ""), str(item.get("report_path") or ""))
        item.setdefault("log_path", item.get("session_log_path", item.get("log_path", "")) or "")
        item.setdefault("created_at", item.get("started_at", item.get("start_time", item.get("ended_at", "n/a"))) or "n/a")
        duration_sec = item.get("duration_sec")
        if duration_sec in (None, "", "n/a"):
            total_ms = item.get("total_duration_ms")
            valid_ms = item.get("valid_duration_ms")
            base_ms = total_ms if total_ms not in (None, "") else valid_ms
            if base_ms not in (None, ""):
                try:
                    duration_sec = round(float(base_ms) / 1000.0, 1)
                except (TypeError, ValueError):
                    duration_sec = "n/a"
            else:
                duration_sec = item.get("elapsed_sec", "n/a")
        item.setdefault("duration_sec", duration_sec or "n/a")
        item.setdefault("behavior_sample_count", item.get("behavior_count", item.get("behavior_sample_count", 0)) or 0)
        item.setdefault("game_event_count", item.get("game_event_count", item.get("event_count", 0)) or 0)
        item.setdefault("warning_count", item.get("warning_count", 0) or 0)
        item.setdefault("error_count", item.get("error_count", 0) or 0)
        return item

    def _compact_report_list_item(self, item: dict[str, Any]) -> dict[str, Any]:
        keys = (
            "session_id",
            "user_id",
            "game_id",
            "status",
            "score",
            "started_at",
            "ended_at",
            "created_at",
            "duration_sec",
            "total_duration_ms",
            "report_path",
            "log_path",
            "report_available",
            "file_index",
            "report_id",
        )
        return {key: item.get(key, "") for key in keys if key in item}

    def _format_report_list_text(self, items: list[dict[str, Any]]) -> str:
        lines: list[str] = []
        for idx, item in enumerate(items, start=1):
            session_id = str(item.get("session_id") or item.get("report_id") or "").strip()
            if not session_id:
                continue
            score = item.get("score", "n/a")
            created_at = item.get("ended_at") or item.get("created_at") or item.get("started_at") or "n/a"
            report_path = item.get("report_path") or item.get("latest_report_path") or item.get("source_report_path") or "n/a"
            lines.append(f"{idx}. {session_id} | score={score} | time={created_at}\n   {report_path}")
        return "\n".join(lines) if lines else "No reports found for current user."

    def _action_log_summary(self, result: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(result, dict):
            return {"result": str(result)[:160]}
        nested = result.get("result") if isinstance(result.get("result"), dict) else result
        detail = nested.get("detail") if isinstance(nested.get("detail"), dict) else {}
        items = nested.get("items") if isinstance(nested.get("items"), list) else []
        return {
            "status": result.get("status", nested.get("status", "")),
            "message": result.get("message", nested.get("message", result.get("reason", ""))),
            "accepted": result.get("accepted", nested.get("accepted", False)),
            "user_id": result.get("user_id", nested.get("user_id", detail.get("user_id", ""))),
            "session_id": result.get("session_id", nested.get("session_id", detail.get("session_id", nested.get("latest_session_id", "")))),
            "report_path": result.get("report_path", nested.get("report_path", nested.get("source_report_path", nested.get("latest_report_path", detail.get("report_path", ""))))),
            "export_path": result.get("export_path", nested.get("export_path", "")),
            "items_count": result.get("items_count", nested.get("items_count", len(items) if items else "")),
        }

    def _session_item_from_state(self) -> dict[str, Any] | None:
        session = self.get_session_state() or {}
        report_path = session.get("latest_report_path") or session.get("report_path") or ""
        session_id = session.get("session_id") or session.get("current_session_id") or ""
        if not session_id and not report_path:
            return None
        item = {
            "session_id": str(session_id or "latest_session"),
            "user_id": str(session.get("user_id") or self.get_app_state().get("current_user_id") or ""),
            "game_id": str(session.get("game_id") or self.get_app_state().get("current_game_id") or ""),
            "status": str(session.get("training_status") or session.get("status") or ("active" if session.get("session_active") else "completed")),
            "score": session.get("score", session.get("score_last", "n/a")),
            "report_path": str(report_path or ""),
            "log_path": str(session.get("log_path") or ""),
            "created_at": str(session.get("started_at") or session.get("created_at") or "n/a"),
            "duration_sec": session.get("duration_sec", round(float(session.get("total_duration_ms", session.get("valid_duration_ms", 0))) / 1000.0, 1) if session.get("total_duration_ms", session.get("valid_duration_ms")) not in (None, "") else session.get("session_elapsed_ms", "n/a")),
            "behavior_sample_count": session.get("behavior_sample_count", 0) or 0,
            "game_event_count": session.get("game_event_count", 0) or 0,
            "warning_count": session.get("warning_count", 0) or 0,
            "error_count": session.get("error_count", 0) or 0,
        }
        return self._normalize_session_record(item)

    def _safe_report_path(self, report_path: str) -> Path | None:
        raw_path = str(report_path or "").strip()
        if not raw_path:
            return None
        path = Path(raw_path)
        if not path.is_absolute():
            path = Path.cwd() / path
        try:
            resolved = path.resolve()
        except OSError:
            return None
        return resolved

    def _read_report_preview(self, report_path: str, max_chars: int = 8000) -> str:
        path = self._safe_report_path(report_path)
        if path is None:
            return ""
        try:
            if path.exists() and path.is_file():
                return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
        except OSError:
            return ""
        return ""

    def _infer_existing_report_path(self, session_id: str = "", report_path: str = "") -> str:
        candidates: list[Path] = []
        raw_report_path = str(report_path or "").strip()
        if raw_report_path:
            safe = self._safe_report_path(raw_report_path)
            if safe is not None:
                candidates.append(safe)
        sid = str(session_id or "").strip()
        if sid:
            # write_session_report() uses reports/sessions/<session_id>.md.
            # Some older DB rows were written before report_path was backfilled;
            # the file can still exist on disk and should be treated as the report.
            candidates.append((Path.cwd() / "reports" / "sessions" / f"{sid}.md").resolve())
        for idx, candidate in enumerate(candidates):
            try:
                if candidate.exists() and candidate.is_file():
                    if idx == 0 and raw_report_path:
                        # Preserve an explicit DB/user supplied report_path exactly as stored.
                        # Windows tests and the GUI compare/display native paths; forcing
                        # Path.as_posix() here changes C:\\... into C:/... and creates
                        # false failures even though the file is valid.  Inferred fallback
                        # paths below still use project-relative POSIX text for stable JSON.
                        return raw_report_path
                    try:
                        return candidate.relative_to(Path.cwd().resolve()).as_posix()
                    except ValueError:
                        return str(candidate)
            except OSError:
                continue
        return raw_report_path

    def _report_item_has_readable_report(self, item: dict[str, Any]) -> bool:
        report_path = str(item.get("report_path") or item.get("latest_report_path") or "").strip()
        if not report_path:
            return False
        path = self._safe_report_path(report_path)
        if path is None:
            return False
        try:
            return path.exists() and path.is_file()
        except OSError:
            return False

    def _fetch_report_session_list(self, user_id: str = "", *, compact: bool = True) -> dict[str, Any]:
        user_id = str(user_id or "").strip()
        items: list[dict[str, Any]] = []
        conn = self._connect_readonly_db()
        try:
            table_name = self._session_table_name(conn)
            if table_name:
                columns = self._table_columns(conn, table_name)
                order_col = ""
                for candidate in ("ended_at", "created_at", "started_at", "start_time"):
                    if candidate in columns:
                        order_col = candidate
                        break
                order_sql = f" ORDER BY {order_col} DESC" if order_col else " ORDER BY rowid DESC"
                if user_id and "user_id" in columns:
                    rows = conn.execute(f"SELECT * FROM {table_name} WHERE user_id=?" + order_sql, (user_id,)).fetchall()
                elif user_id:
                    rows = []
                else:
                    rows = conn.execute(f"SELECT * FROM {table_name}" + order_sql).fetchall()
                items = [self._normalize_session_record(dict(row)) for row in rows]
        finally:
            conn.close()

        state_item = self._session_item_from_state()
        if state_item and (not user_id or str(state_item.get("user_id") or "") in {"", user_id}):
            existing_ids = {str(item.get("session_id") or "") for item in items}
            if state_item.get("session_id") not in existing_ids:
                items.insert(0, state_item)

        # Report page is scoped to the current user.  Do not leak other users'
        # sessions through fallback records or stale profile/session state.
        if user_id:
            items = [item for item in items if str(item.get("user_id") or "") in {"", user_id}]

        # The Report page should operate on reports, not arbitrary sessions.
        # Older rows may be valid sessions without report_path; leaving them as the
        # default selector caused Show Selected/Export to target a no-report session
        # after switching users.  Keep only entries with a readable report file.
        report_items: list[dict[str, Any]] = []
        for item in items:
            item["report_path"] = self._infer_existing_report_path(str(item.get("session_id") or ""), str(item.get("report_path") or ""))
            item["report_available"] = self._report_item_has_readable_report(item)
            if item["report_available"]:
                report_items.append(item)

        items = report_items
        for i, item in enumerate(items, start=1):
            item["file_index"] = i
            item["report_id"] = item.get("session_id", "")
            item["report_available"] = True

        self._last_report_list = deepcopy(items)
        public_items = [self._compact_report_list_item(item) for item in items] if compact else items
        return {
            "status": "accepted",
            "message": "report_list",
            "user_id": user_id,
            "items": public_items,
            "sessions": public_items,
            "items_count": len(items),
            "session_count": len(items),
            "report_list_text": self._format_report_list_text(public_items),
        }

    def _resolve_report_session_detail(self, user_id: str, session_id: str = "", report_path: str = "", file_index: Any = None) -> dict[str, Any]:
        user_id = str(user_id or "").strip()
        session_id = str(session_id or "").strip()
        report_path = str(report_path or "").strip()
        report_path_norm = str(Path(report_path).as_posix()) if report_path else ""
        listing = self._fetch_report_session_list(user_id, compact=False)
        items = listing.get("items", []) if isinstance(listing, dict) else []

        if file_index not in (None, "", "n/a"):
            try:
                idx = int(file_index)
            except (TypeError, ValueError):
                idx = -1
            if 1 <= idx <= len(items):
                return dict(items[idx - 1])

        for item in items:
            item_session_id = str(item.get("session_id") or "").strip()
            item_report_path = str(item.get("report_path") or "").strip()
            item_report_path_norm = str(Path(item_report_path).as_posix()) if item_report_path else ""
            if session_id and item_session_id == session_id:
                return dict(item)
            if report_path_norm and item_report_path_norm == report_path_norm:
                return dict(item)

        # Strict user-scoped DB fallback.  It is valid only when the table itself
        # confirms the same user_id.  This avoids the TEST_NEW -> TEST leakage that
        # happened during early card migration.
        if session_id:
            conn = self._connect_readonly_db()
            try:
                table_name = self._session_table_name(conn)
                if table_name:
                    columns = self._table_columns(conn, table_name)
                    id_col = "session_id" if "session_id" in columns else ("id" if "id" in columns else "")
                    if id_col:
                        if user_id and "user_id" in columns:
                            row = conn.execute(f"SELECT * FROM {table_name} WHERE {id_col}=? AND user_id=?", (session_id, user_id)).fetchone()
                        elif user_id:
                            row = None
                        else:
                            row = conn.execute(f"SELECT * FROM {table_name} WHERE {id_col}=?", (session_id,)).fetchone()
                        if row:
                            return self._normalize_session_record(dict(row))
            finally:
                conn.close()

        return {}

    def _fetch_report_session_detail(self, session_id: str = "", user_id: str = "", report_path: str = "", file_index: Any = None) -> dict[str, Any]:
        session_id = str(session_id or "").strip()
        report_path = str(report_path or "").strip()
        user_id = str(user_id or "").strip()
        if not session_id and not report_path and file_index in (None, "", "n/a"):
            return {"status": "missing_input", "message": "missing_session_id", "result": "missing_report_identifier", "session_id": "", "user_id": user_id}

        detail = self._resolve_report_session_detail(user_id, session_id=session_id, report_path=report_path, file_index=file_index)
        if detail:
            detail = dict(detail)
            detail_user_id = str(detail.get("user_id") or "").strip()
            if user_id and detail_user_id and detail_user_id != user_id:
                return {"status": "report_user_mismatch", "message": "report_user_mismatch", "session_id": session_id or detail.get("session_id", ""), "user_id": user_id, "report_user_id": detail_user_id}
            detail["report_path"] = self._infer_existing_report_path(str(detail.get("session_id") or ""), str(detail.get("report_path") or ""))
            detail["status"] = "accepted"
            detail["message"] = "report_loaded"
            detail["report_preview"] = self._read_report_preview(str(detail.get("report_path") or ""))
            detail["report_available"] = self._report_item_has_readable_report(detail)
            detail.setdefault("report_id", detail.get("session_id", ""))
            self._last_report_detail = deepcopy(detail)
            return detail

        return {"status": "session_not_found", "message": "session_not_found", "session_id": session_id, "report_path": report_path, "user_id": user_id}

    def _fetch_latest_report_summary(self, user_id: str = "") -> dict[str, Any]:
        user_id = str(user_id or "").strip()
        listing = self._fetch_report_session_list(user_id, compact=False)
        items = listing.get("items", []) if isinstance(listing, dict) else []
        if items:
            first = dict(items[0])
            detail = self._fetch_report_session_detail(str(first.get("session_id") or ""), user_id)
            if detail.get("status") == "accepted":
                return {
                    "status": "accepted",
                    "message": "latest_report_loaded",
                    "user_id": user_id,
                    "latest_session_id": detail.get("session_id", ""),
                    "latest_report_path": detail.get("report_path", ""),
                    "report_available": bool(detail.get("report_path")),
                    "detail": detail,
                    "report": detail,
                    "report_preview": detail.get("report_preview", ""),
                    "items_count": listing.get("items_count", len(items)),
                }

        return {
            "status": "no_report_available",
            "message": "no_report_available",
            "user_id": user_id,
            "latest_session_id": "",
            "latest_report_path": "",
            "report_available": False,
            "items_count": 0,
        }

    def _refresh_report_summary(self, user_id: str = "") -> dict[str, Any]:
        latest = self._fetch_latest_report_summary(user_id)
        if latest.get("status") == "accepted":
            latest["message"] = "report_refreshed"
            return latest
        session = self.get_session_state() or {}
        latest_report_path = str(session.get("latest_report_path") or session.get("report_path") or "")
        latest_session_id = str(session.get("session_id") or session.get("current_session_id") or "")
        state_user = str(session.get("user_id") or self.get_app_state().get("current_user_id") or "")
        if user_id and state_user and state_user != user_id:
            latest_report_path = ""
            latest_session_id = ""
        report_available = bool(latest_report_path)
        summary = {
            "status": "accepted",
            "message": "report_refreshed",
            "user_id": str(user_id or state_user or ""),
            "latest_report_path": latest_report_path,
            "latest_session_id": latest_session_id,
            "report_available": report_available,
            "reason": "report_available" if report_available else "no_report_available",
            "session": session,
            "report_preview": self._read_report_preview(latest_report_path),
        }
        if report_available:
            self._last_report_detail = deepcopy(summary)
        return summary

    def _export_report_txt(self, user_id: str = "", session_id: str = "", report_path: str = "", file_index: Any = None, out_dir: str = "reports/exports", allow_latest_fallback: bool = False) -> dict[str, Any]:
        user_id = str(user_id or "").strip()
        detail = self._fetch_report_session_detail(session_id=session_id, user_id=user_id, report_path=report_path, file_index=file_index)
        if allow_latest_fallback and not report_path and (detail.get("status") != "accepted" or not self._report_item_has_readable_report(detail)):
            latest = self._fetch_latest_report_summary(user_id)
            latest_detail = latest.get("detail") if isinstance(latest.get("detail"), dict) else {}
            if latest.get("status") == "accepted" and latest_detail:
                detail = dict(latest_detail)
                detail["status"] = "accepted"
                detail["message"] = "latest_report_fallback_loaded"
        if detail.get("status") != "accepted":
            return {"status": detail.get("status", "report_not_found"), "message": detail.get("message", "report_not_found"), "accepted": False, "user_id": user_id, "detail": detail}
        source_report_path = str(detail.get("report_path") or "").strip()
        if not source_report_path:
            return {"status": "report_not_found", "message": "report_path_missing", "accepted": False, "user_id": user_id, "detail": detail}
        text = self._read_report_preview(source_report_path, max_chars=200000)
        if not text:
            return {"status": "report_not_found", "message": "report_file_not_readable", "accepted": False, "user_id": user_id, "source_report_path": source_report_path, "detail": detail}
        session_id_safe = str(detail.get("session_id") or "report").replace("/", "_").replace("\\", "_").replace(":", "_")
        out_root = Path(out_dir)
        if not out_root.is_absolute():
            out_root = Path.cwd() / out_root
        out_root.mkdir(parents=True, exist_ok=True)
        export_path = out_root / f"{session_id_safe}.txt"
        export_text = text
        try:
            export_path.write_text(export_text, encoding="utf-8")
        except OSError as exc:
            return {"status": "export_failed", "message": str(exc), "accepted": False, "user_id": user_id, "source_report_path": source_report_path}
        self._last_export_path = export_path.as_posix()
        result = {
            "status": "accepted",
            "message": "report_exported_txt",
            "accepted": True,
            "user_id": user_id,
            "session_id": detail.get("session_id", ""),
            "source_report_path": source_report_path,
            "export_path": export_path.as_posix(),
            "bytes_written": export_path.stat().st_size,
            "detail": detail,
            "report": detail,
        }
        self._last_report_detail = deepcopy(detail)
        return result



    def _select_game_summary(self, game_id: str) -> dict[str, Any]:
        game_id = str(game_id or "").strip()
        if game_id not in {"trace_lock"}:
            return {
                "status": "unsupported_game",
                "message": "only_existing_trace_lock_is_exposed_in_task24b",
                "accepted": False,
                "game_id": game_id,
                "supported_game_ids": ["trace_lock"],
            }

        previous_game_id = str(self.get_app_state().get("current_game_id") or self.get_game_hud().get("game_id") or "")
        self._render_resources = self._build_safe_render_resources(game_id=game_id)

        # Keep using the existing live-control/game client pipeline. This does not create a
        # second game route: it swaps the existing source client to the already-registered
        # TraceLock client and preserves the current session id when possible.
        if self._live_control_source:
            source = self._live_control_source
            if getattr(source, "interaction_enabled", False) and source.game_id != game_id:
                return {
                    "status": "active_session_requires_stop",
                    "message": "stop_current_session_before_switching_game",
                    "accepted": False,
                    "game_id": game_id,
                    "previous_game_id": previous_game_id,
                }

            if source.game_id != game_id or getattr(source, "_client", None) is None:
                source.game_id = game_id
                try:
                    source._client = create_game_client(game_id)
                except Exception as exc:
                    return {
                        "status": "select_failed",
                        "message": f"failed_to_create_existing_game_client: {exc}",
                        "accepted": False,
                        "game_id": game_id,
                        "previous_game_id": previous_game_id,
                    }
            else:
                source.game_id = game_id

            if hasattr(source, "last_game_view"):
                try:
                    source.last_game_view = source.get_game_view()
                except Exception:
                    source.last_game_view = {}
            return {
                "status": "accepted",
                "message": "game_selected",
                "accepted": True,
                "game_id": game_id,
                "previous_game_id": previous_game_id,
                "game_hud": self.get_game_hud(),
                "render_resources": self.get_render_resources(),
                "selection_note": "existing_client_preserved" if previous_game_id == game_id else "existing_registered_client_selected",
            }

        if self._core_source:
            return {
                "status": "not_implemented",
                "message": "game_selection_requires_live_control_or_mock",
                "accepted": False,
                "game_id": game_id,
                "previous_game_id": previous_game_id,
            }

        if self._live_source:
            return {
                "status": "readonly_not_allowed",
                "message": "game_selection_requires_control_mode",
                "accepted": False,
                "game_id": game_id,
                "previous_game_id": previous_game_id,
            }

        self._app_state["current_game_id"] = game_id
        self._session_state["game_id"] = game_id
        return {
            "status": "accepted",
            "message": "game_selected",
            "accepted": True,
            "game_id": game_id,
            "previous_game_id": previous_game_id,
            "game_hud": self.get_game_hud(),
            "render_resources": self.get_render_resources(),
        }

    def _set_game_difficulty_summary(self, game_id: str, mode: str = "auto", level: Any = None) -> dict[str, Any]:
        game_id = str(game_id or self.get_app_state().get("current_game_id") or self.get_game_hud().get("game_id") or "").strip()
        if game_id != "trace_lock":
            return {
                "status": "unsupported_game",
                "message": "difficulty_control_only_exposes_existing_trace_lock",
                "accepted": False,
                "game_id": game_id,
                "supported_game_ids": ["trace_lock"],
            }

        raw_mode = str(mode or "").strip().lower()
        raw_level_text = str(level).strip().lower() if level is not None else ""
        auto_like_level = level is None or raw_level_text in {"", "auto", "dynamic", "none", "null", "nan"}

        # Some UI paths may send AUTO through the level/debug field while mode
        # is empty or stale.  Prefer explicit AUTO tokens over stale defaults.
        if raw_mode in {"auto", "dynamic"} or (raw_mode not in {"manual"} and auto_like_level):
            mode = "auto"
        elif raw_mode == "manual":
            mode = "manual"
        elif auto_like_level:
            mode = "auto"
        else:
            mode = "manual"

        debug_level: int | None
        if mode == "auto":
            debug_level = None
        else:
            try:
                debug_level = max(1, min(5, int(level)))
            except (TypeError, ValueError):
                return {
                    "status": "missing_input",
                    "message": "missing_or_invalid_difficulty_level",
                    "accepted": False,
                    "game_id": game_id,
                    "difficulty_mode": mode,
                    "raw_mode": raw_mode,
                    "raw_level": level,
                }

        previous_game_id = str(self.get_app_state().get("current_game_id") or self.get_game_hud().get("game_id") or "")
        if previous_game_id != "trace_lock":
            select_summary = self._select_game_summary("trace_lock")
            if select_summary.get("status") != "accepted":
                return {
                    "status": select_summary.get("status", "select_failed"),
                    "message": select_summary.get("message", "trace_lock_select_failed"),
                    "accepted": False,
                    "game_id": game_id,
                    "difficulty_mode": mode,
                    "select": select_summary,
                }

        if self._live_control_source:
            summary = self._live_control_source.set_debug_difficulty(debug_level)
            accepted = bool(summary.get("accepted", False)) and summary.get("status") == "accepted"
            hud = self.get_game_hud()
            return {
                "status": summary.get("status", "accepted"),
                "message": summary.get("message", "difficulty_updated"),
                "accepted": accepted,
                "game_id": "trace_lock",
                "difficulty_mode": "auto" if debug_level is None else "manual",
                "debug_difficulty": "auto" if debug_level is None else debug_level,
                "level": hud.get("level", debug_level if debug_level is not None else "auto"),
                "game_hud": hud,
                "detail": summary,
            }

        if self._live_source:
            return {
                "status": "readonly_not_allowed",
                "message": "difficulty_control_requires_control_mode",
                "accepted": False,
                "game_id": "trace_lock",
                "difficulty_mode": mode,
            }

        if self._core_source:
            # Core-control already has its own mouse routing tests. Keep TASK24C difficulty
            # control on the GUI live/mock side unless a runtime API is added later.
            return {
                "status": "not_implemented",
                "message": "difficulty_control_not_implemented_for_core_source",
                "accepted": False,
                "game_id": "trace_lock",
                "difficulty_mode": mode,
            }

        # Mock facade: keep the action testable without constructing a second game pipe.
        self._app_state["current_game_id"] = "trace_lock"
        self._session_state["game_id"] = "trace_lock"
        return {
            "status": "accepted",
            "message": "difficulty_updated",
            "accepted": True,
            "game_id": "trace_lock",
            "difficulty_mode": "auto" if debug_level is None else "manual",
            "debug_difficulty": "auto" if debug_level is None else debug_level,
            "level": debug_level if debug_level is not None else "auto",
            "game_hud": self.get_game_hud(),
        }


    def get_control_manifest(self) -> list[dict[str, Any]]:
        readonly = self.mode in {"core", "live-readonly"}
        mode = self.mode
        def item(action_id: str, label: str, category: str, supported: bool, readonly_allowed: bool, live_control_required: bool, description: str) -> dict[str, Any]:
            enabled = supported and (readonly_allowed or not readonly)
            if live_control_required and mode != "live-control":
                enabled = False
            return {"action_id": action_id, "label": label, "category": category, "enabled": enabled, "supported": supported, "readonly_allowed": readonly_allowed, "live_control_required": live_control_required, "description": description}
        return [
            item("app.refresh_now", "Refresh", "app", True, True, False, "refresh snapshots"),
            item("app.quit", "Quit", "app", True, True, False, "quit app"),
            item("live.reconnect", "Reconnect", "live", self.mode in {"live-readonly", "live-control"}, True, False, "reconnect live source"),
            item("live.safe_stop", "Safe Stop", "live", self.mode == "live-control", False, True, "safe stop current action (live-control backend required)"),
            item("user.load_current", "Load Current User", "user", True, True, False, "load current user from run args"),
            item("user.ensure_demo_debug", "Ensure Demo User (Debug)", "user", True, False, False, "debug fallback only"),
            item("user.show_profile", "Show Profile", "user", True, True, False, "show current profile"),
            item("calibration.start", "Start Calibration", "calibration", False, False, False, "not implemented: requires calibration workflow/progress UI"),
            item("calibration.status", "Calibration Status", "calibration", True, True, False, "show calibration status"),
            item("session.start", "Start Session", "session", True, False, False, "start mock/debug/training session"),
            item("session.stop", "Stop Session", "session", True, False, False, "stop current session"),
            item("session.status", "Session Status", "session", True, True, False, "show session status"),
            item("game.status", "Game Status", "game", True, True, False, "show game hud/state"),
            item("game.select", "Select Game", "game", True, False, False, "select existing registered game client"),
            item("game.difficulty", "TraceLock Difficulty", "game", True, False, False, "set TraceLock manual difficulty or reset auto difficulty"),
            item("diagnostics.clear_last_error", "Clear Last Error", "diagnostics", True, True, False, "clear last command error"),
            item("diagnostics.refresh", "Refresh Diagnostics", "diagnostics", True, True, False, "refresh diagnostics")
        ]

    def _current_user_id_for_control_state(self, app: dict[str, Any]) -> str:
        override = str(getattr(self, "_current_user_override", "") or "").strip()
        if override:
            return override
        return str(app.get("current_user_id") or app.get("user_id") or "").strip()

    def _baseline_user_profile_context(self, user_id: str) -> dict[str, Any]:
        user_id = str(user_id or "").strip()
        if not user_id:
            return {}
        profile = self._fetch_profile_summary(user_id)
        calibration = self._fetch_calibration_status(user_id)
        merged: dict[str, Any] = {}
        if isinstance(profile, dict):
            merged.update(profile)
        if isinstance(calibration, dict):
            merged.update({
                "calibration_status": calibration.get("calibration_status", calibration.get("status", "")),
                "calibration_usable": calibration.get("calibration_usable", calibration.get("latest_valid", "")),
                "latest_valid": calibration.get("latest_valid", calibration.get("valid", "")),
                "attention_baseline": calibration.get("attention_baseline", "n/a"),
                "gyro_noise_rms": calibration.get("gyro_noise_rms", "n/a"),
                "failure_reason": calibration.get("failure_reason", ""),
            })
            if not merged.get("last_calibration_id") or merged.get("last_calibration_id") == "n/a":
                merged["last_calibration_id"] = calibration.get("last_calibration_id", "n/a")
        return merged

    def _calibration_options_text_for_user(self, user_id: str) -> tuple[str, str]:
        user_id = str(user_id or "").strip()
        options: list[str] = []
        if user_id:
            listing = self._fetch_calibration_list(user_id)
            raw_items = listing.get("items") or listing.get("calibrations") or []
            if isinstance(raw_items, list):
                for item in raw_items:
                    if not isinstance(item, dict):
                        continue
                    if str(item.get("user_id") or "").strip() != user_id:
                        continue
                    cal_id = str(item.get("calibration_id") or "").strip()
                    if cal_id and cal_id not in options:
                        options.append(cal_id)
        if not options:
            return "no_report_available", "no_report_available"
        return "|".join(options), options[0]

    def _report_options_text_for_user(self, user_id: str) -> tuple[str, str]:
        user_id = str(user_id or "").strip()
        listing = self._fetch_report_session_list(user_id)
        options: list[str] = []
        raw_items = listing.get("items") or listing.get("sessions") or []
        if isinstance(raw_items, list):
            for item in raw_items:
                if not isinstance(item, dict):
                    continue
                if user_id and str(item.get("user_id") or "").strip() not in {"", user_id}:
                    continue
                sid = str(item.get("session_id") or "").strip()
                if sid and sid not in options:
                    options.append(sid)
        if not options:
            return "no_report_available", "no_report_available"
        return "|".join(options), options[0]

    def _hydrate_report_layout_payload(self, payload: dict[str, Any], control_state: dict[str, Any]) -> None:
        if not isinstance(payload, dict) or not isinstance(control_state, dict):
            return
        self._hydrate_layout_payload_from_control_state(payload, control_state)
        current_user_id = str(control_state.get("current_user_id") or self._current_user_id_for_control_state(self.get_app_state()) or "").strip()
        options_text, default_session_id = self._report_options_text_for_user(current_user_id)
        options = [item for item in options_text.split("|") if item]
        candidate = str(control_state.get("report_selected_session_id") or control_state.get("latest_session_id") or "").strip()
        if candidate not in options or candidate == "n/a":
            candidate = default_session_id if default_session_id in options else "no_report_available"
        active_session_id = candidate or "no_report_available"
        card_count = int(payload.get("card_count") or 0)
        for card_index in range(1, card_count + 1):
            for widget_index in range(1, 7):
                prefix = f"card{card_index}_widget{widget_index}"
                widget_id = str(payload.get(f"{prefix}_id") or "")
                if widget_id in {"report_current_user", "report_user_id"}:
                    payload[f"{prefix}_value"] = current_user_id
                    payload[f"{prefix}_fallback"] = current_user_id or "current user"
                elif widget_id in {"report_selector", "selected_report_id", "selected_session_id"}:
                    payload[f"{prefix}_options_text"] = options_text
                    payload[f"{prefix}_value"] = active_session_id
                    payload[f"{prefix}_fallback"] = active_session_id
                elif widget_id in {"selected_report_path", "latest_report_path"}:
                    selected_path = str(control_state.get("report_selected_report_path") or control_state.get("latest_report_path") or "").strip()
                    payload[f"{prefix}_value"] = selected_path or "n/a"
                    payload[f"{prefix}_fallback"] = selected_path or "n/a"
                elif widget_id == "export_path":
                    export_path = str(control_state.get("report_export_path") or "").strip()
                    payload[f"{prefix}_value"] = export_path or "n/a"
                    payload[f"{prefix}_fallback"] = export_path or "n/a"

    def _hydrate_calibration_layout_payload(self, payload: dict[str, Any], control_state: dict[str, Any]) -> None:
        if not isinstance(payload, dict) or not isinstance(control_state, dict):
            return
        self._hydrate_layout_payload_from_control_state(payload, control_state)
        current_user_id = str(control_state.get("current_user_id") or self._current_user_id_for_control_state(self.get_app_state()) or "").strip()
        options_text, default_calibration_id = self._calibration_options_text_for_user(current_user_id)
        options = [item for item in options_text.split("|") if item]

        # The active selector value must be one of the current user's own records.
        # Do not insert controlStateJson.last_calibration_id into the selector when
        # it is not part of this user's list; that is exactly how TEST_NEW can be
        # offered TEST's calibration after a polluted binding.
        candidate = str(control_state.get("calibration_id") or control_state.get("last_calibration_id") or "").strip()
        if candidate not in options or candidate == "n/a":
            candidate = default_calibration_id if default_calibration_id in options else "manual"
        active_calibration_id = candidate or "manual"

        card_count = int(payload.get("card_count") or 0)
        for card_index in range(1, card_count + 1):
            for widget_index in range(1, 7):
                prefix = f"card{card_index}_widget{widget_index}"
                widget_id = str(payload.get(f"{prefix}_id") or "")
                if widget_id == "calibration_user_id":
                    payload[f"{prefix}_value"] = current_user_id
                    payload[f"{prefix}_fallback"] = current_user_id or "current user"
                elif widget_id == "selected_calibration_id":
                    payload[f"{prefix}_options_text"] = options_text
                    payload[f"{prefix}_value"] = active_calibration_id
                    payload[f"{prefix}_fallback"] = active_calibration_id
                elif widget_id == "manual_calibration_id":
                    payload[f"{prefix}_value"] = "" if active_calibration_id == "manual" else active_calibration_id
                    payload[f"{prefix}_fallback"] = "Paste calibration id"

    def _hydrate_layout_payload_from_control_state(self, payload: dict[str, Any], control_state: dict[str, Any]) -> None:
        if not isinstance(payload, dict) or not isinstance(control_state, dict):
            return
        card_count = int(payload.get("card_count") or 0)
        for card_index in range(1, card_count + 1):
            for widget_index in range(1, 7):
                prefix = f"card{card_index}_widget{widget_index}"
                source = str(payload.get(f"{prefix}_source") or "")
                if source.startswith("controlStateJson.") or source.startswith("controlState."):
                    field_name = source.split(".", 1)[1]
                    value = control_state.get(field_name)
                    if value is not None and value != "":
                        payload[f"{prefix}_value"] = str(value)

    def get_control_state(self) -> dict[str, Any]:
        app = self.get_app_state()
        session = self.get_session_state()
        now = int(time.time() * 1000)
        session_active = bool(session.get("session_active"))
        session_elapsed_ms = session.get("session_elapsed_ms")
        if session_active:
            base_start = self._active_session_started_at_ms or session.get("started_at_ms")
            if base_start:
                session_elapsed_ms = max(0, now - int(base_start))
        last_result = self.last_command_result if isinstance(self.last_command_result, dict) else {}
        last_command_id = self.last_command.get("command", "") if isinstance(self.last_command, dict) else ""
        detail = last_result.get("detail") if isinstance(last_result.get("detail"), dict) else {}
        calibration_detail = last_result.get("calibration") if isinstance(last_result.get("calibration"), dict) else {}
        profile_detail = last_result.get("profile") if isinstance(last_result.get("profile"), dict) else {}
        report_detail = last_result.get("report") if isinstance(last_result.get("report"), dict) else {}
        result_detail = last_result.get("result") if isinstance(last_result.get("result"), dict) else {}
        progress_detail = last_result.get("progress") if isinstance(last_result.get("progress"), dict) else {}
        current_user_id = self._current_user_id_for_control_state(app)
        baseline_detail = self._baseline_user_profile_context(current_user_id)
        progress_baseline = self._calibration_progress_summary()
        merged_detail: dict[str, Any] = {}
        for src in (baseline_detail, progress_baseline, result_detail, progress_detail, detail, calibration_detail, profile_detail, report_detail, last_result):
            if isinstance(src, dict):
                src_user = str(src.get("user_id") or src.get("current_user_id") or "").strip()
                if src_user and current_user_id and src_user != current_user_id:
                    continue
                merged_detail.update(src)

        report_options_text, _report_default_session_id = self._report_options_text_for_user(current_user_id)
        report_list_text = str(merged_detail.get("report_list_text") or "")
        if not report_list_text:
            report_list_text = self._format_report_list_text(self._last_report_list) if self._last_report_list else "Click Refresh Report List to show report names."
        last_action_id = str(last_result.get("action_id") or last_command_id or "")
        if last_action_id in {"report.export", "report.export_txt"}:
            report_export_path = str(merged_detail.get("export_path") or "")
        elif last_action_id.startswith("report."):
            report_export_path = ""
        else:
            report_export_path = self._last_export_path

        return {
            "mode": self.mode,
            "control_enabled": self.mode != "core",
            "readonly": self.mode in {"core", "live-readonly"},
            "current_user_id": current_user_id,
            "current_session_id": session.get("session_id", "") or ("session_id_unavailable" if session_active else ""),
            "current_game_id": app.get("current_game_id", session.get("game_id", "")),
            "session_active": session_active,
            "calibration_active": bool(progress_baseline.get("running", False)),
            "live_connected": app.get("connection_status") == "connected" or app.get("source") in {"live_readonly", "live_control"},
            "last_command": self.last_command.get("command", "") if isinstance(self.last_command, dict) else "",
            "last_command_result": self.last_command_result.get("status", "") if isinstance(self.last_command_result, dict) else "",
            "last_command_error": self._last_command_error,
            "command_count": self.command_count,
            "last_action_id": last_command_id,
            "last_action_status": str(last_result.get("status", "")),
            "last_action_message": str(last_result.get("message", last_result.get("reason", ""))),
            "last_action_accepted": bool(last_result.get("accepted", False)),
            "last_action_result": str(last_result.get("result", ""))[:240],
            "latest_report_path": merged_detail.get("latest_report_path", session.get("latest_report_path") or session.get("report_path") or ""),
            "report_selected_session_id": merged_detail.get("session_id", merged_detail.get("latest_session_id", "")),
            "report_selected_report_path": merged_detail.get("report_path", merged_detail.get("source_report_path", merged_detail.get("latest_report_path", session.get("report_path") or session.get("latest_report_path") or ""))),
            "report_selected_user_id": merged_detail.get("user_id", ""),
            "report_available": merged_detail.get("report_available", bool(merged_detail.get("report_path") or merged_detail.get("source_report_path") or merged_detail.get("latest_report_path") or session.get("report_path") or session.get("latest_report_path"))),
            "report_export_path": report_export_path,
            "report_preview": merged_detail.get("report_preview", ""),
            "report_selected_report_preview": merged_detail.get("report_preview", ""),
            "report_preview_available": bool(merged_detail.get("report_preview", "")),
            "report_options_text": report_options_text,
            "report_list_text": report_list_text,
            "app_elapsed_ms": now - self._started_at_ms,
            "session_elapsed_ms": session_elapsed_ms if session_active else "n/a",
            "last_session_status": session.get("training_status", "none"),
            "profile_status": merged_detail.get("profile_status", str(last_result.get("status", "")) if last_command_id == "user.show_profile" else ""),
            "user_type": merged_detail.get("user_type", ""),
            "profile_loaded": merged_detail.get("profile_loaded", ""),
            "attention_low_threshold": merged_detail.get("attention_low_threshold", "n/a"),
            "attention_high_threshold": merged_detail.get("attention_high_threshold", "n/a"),
            "preferred_game_id": merged_detail.get("preferred_game_id", "n/a"),
            "difficulty_level": merged_detail.get("difficulty_level", "n/a"),
            "last_calibration_id": merged_detail.get("last_calibration_id", merged_detail.get("calibration_id", "n/a")),
            "calibration_id": merged_detail.get("calibration_id", merged_detail.get("last_calibration_id", "n/a")),
            "calibration_status": merged_detail.get("calibration_status", str(last_result.get("status", "")) if str(last_command_id).startswith("calibration.") else ""),
            "calibration_usable": merged_detail.get("calibration_usable", merged_detail.get("latest_valid", merged_detail.get("valid", ""))),
            "latest_valid": merged_detail.get("latest_valid", merged_detail.get("valid", "")),
            "failure_reason": merged_detail.get("failure_reason", ""),
            "attention_baseline": merged_detail.get("attention_baseline", ""),
            "attention_std": merged_detail.get("attention_std", ""),
            "gyro_noise_rms": merged_detail.get("gyro_noise_rms", ""),
            "calibration_progress_status": progress_baseline.get("status", progress_detail.get("status", "idle")),
            "calibration_progress_running": progress_baseline.get("running", progress_detail.get("running", False)),
            "calibration_running": progress_baseline.get("running", progress_detail.get("running", False)),
            "calibration_progress_phase": progress_baseline.get("current_phase", progress_detail.get("current_phase", "n/a")),
            "calibration_phase": progress_baseline.get("current_phase", progress_detail.get("current_phase", "n/a")),
            "calibration_progress_exit_code": progress_baseline.get("exit_code", progress_detail.get("exit_code", "n/a")),
            "calibration_progress_output_count": progress_baseline.get("output_count", progress_detail.get("output_count", 0)),
            "calibration_progress_elapsed_sec": progress_baseline.get("elapsed_sec", progress_detail.get("elapsed_sec", "n/a")),
            "calibration_progress_remaining_sec": progress_baseline.get("remaining_sec", progress_detail.get("remaining_sec", "n/a")),
            "calibration_phase_remaining_sec": progress_baseline.get("remaining_sec", progress_detail.get("remaining_sec", "n/a")),
            "calibration_total_remaining_sec": progress_baseline.get("total_remaining_sec", progress_detail.get("total_remaining_sec", "n/a")),
            "calibration_progress_fraction": progress_baseline.get("progress_fraction", progress_detail.get("progress_fraction", 0.0)),
            "calibration_progress_percent": progress_baseline.get("progress_percent", progress_detail.get("progress_percent", 0.0)),
            "calibration_phase_prompt_text": progress_baseline.get("phase_prompt_text", progress_detail.get("phase_prompt_text", "")),
            "calibration_operator_guidance": progress_baseline.get("operator_guidance", progress_detail.get("operator_guidance", progress_baseline.get("phase_prompt_text", ""))),
            "calibration_active_prompt_text": progress_baseline.get("active_prompt_text", progress_detail.get("active_prompt_text", "")),
            "calibration_phase_title": (progress_baseline.get("current_phase_detail") or progress_detail.get("current_phase_detail") or {}).get("title", "n/a") if isinstance(progress_baseline.get("current_phase_detail") or progress_detail.get("current_phase_detail"), dict) else "n/a",
            "calibration_phase_instruction": (progress_baseline.get("current_phase_detail") or progress_detail.get("current_phase_detail") or {}).get("user_instruction", "n/a") if isinstance(progress_baseline.get("current_phase_detail") or progress_detail.get("current_phase_detail"), dict) else "n/a",
            "calibration_phase_avoid_instruction": (progress_baseline.get("current_phase_detail") or progress_detail.get("current_phase_detail") or {}).get("avoid_instruction", "n/a") if isinstance(progress_baseline.get("current_phase_detail") or progress_detail.get("current_phase_detail"), dict) else "n/a",
            "calibration_phase_duration_hint": (progress_baseline.get("current_phase_detail") or progress_detail.get("current_phase_detail") or {}).get("duration_hint", "n/a") if isinstance(progress_baseline.get("current_phase_detail") or progress_detail.get("current_phase_detail"), dict) else "n/a",
            "items_count": merged_detail.get("items_count", merged_detail.get("session_count", merged_detail.get("user_count", merged_detail.get("calibration_count", "")))),
            "session_count": merged_detail.get("session_count", merged_detail.get("items_count", "")),
            "latest_session_id": merged_detail.get("latest_session_id", merged_detail.get("session_id", session.get("session_id", ""))),
        }

    def _set_current_user_context(self, user_id: str, display_name: str | None = None, user_type: str = "local_user") -> None:
        if not user_id:
            return
        self._current_user_override = str(user_id)
        if self._live_control_source:
            self._live_control_source.user_id = user_id
            return
        if self._core_source or self._live_source:
            return
        self._app_state["current_user_id"] = user_id
        self._app_state["current_user_name"] = display_name or user_id
        self._app_state["user_type"] = user_type

    def _list_users_summary(self) -> dict[str, Any]:
        store = SqliteStore(self.db_path)
        store.connect()
        try:
            users = store.list_users()
            normalized = []
            for user in users:
                item = dict(user)
                item.setdefault("display_name", item.get("user_id", ""))
                item.setdefault("user_type", "local_user")
                normalized.append(item)
            return {
                "status": "accepted",
                "message": "user_list",
                "user_count": len(normalized),
                "items_count": len(normalized),
                "users": normalized,
                "items": normalized,
            }
        finally:
            store.close()

    def _create_user_summary(self, user_id: str, display_name: str) -> dict[str, Any]:
        if not user_id:
            return {"status": "missing_input", "message": "missing_user_id", "user_id": ""}
        store = SqliteStore(self.db_path)
        store.connect()
        try:
            existing = store.get_user(user_id)
            if existing:
                self._set_current_user_context(user_id, str(existing.get("display_name") or display_name or user_id), str(existing.get("user_type") or "local_user"))
                return {
                    "status": "accepted",
                    "message": "user_exists",
                    "user_id": user_id,
                    "display_name": existing.get("display_name") or display_name or user_id,
                    "user_type": existing.get("user_type") or "local_user",
                }
            user = {
                "user_id": user_id,
                "display_name": display_name or user_id,
                "user_type": "local_user",
                "created_at": "",
                "last_login_at": "",
            }
            store.upsert_user(user)
            self._set_current_user_context(user_id, display_name or user_id, "local_user")
            return {
                "status": "created",
                "message": "user_created",
                "user_id": user_id,
                "display_name": display_name or user_id,
                "user_type": "local_user",
            }
        finally:
            store.close()

    def _load_user_summary(self, user_id: str) -> dict[str, Any]:
        if not user_id:
            return {"status": "missing_input", "message": "missing_user_id", "user_id": ""}
        store = SqliteStore(self.db_path)
        store.connect()
        try:
            user = store.get_user(user_id)
            if user:
                display_name = str(user.get("display_name") or user_id)
                user_type = str(user.get("user_type") or "local_user")
                self._set_current_user_context(user_id, display_name, user_type)
                profile = self._fetch_profile_summary(user_id)
                return {
                    "status": "user_loaded",
                    "message": "user_loaded",
                    "user_id": user_id,
                    "display_name": display_name,
                    "user_type": user_type,
                    "profile": profile,
                }
        finally:
            store.close()
        self._set_current_user_context(user_id, user_id, "local_user")
        return {
            "status": "user_loaded",
            "message": "user_loaded_without_persisted_profile",
            "user_id": user_id,
            "display_name": user_id,
            "user_type": "local_user",
            "profile": {
                "status": "profile_not_found",
                "message": "profile_not_found",
                "current_user_id": user_id,
                "user_type": "local_user",
                "profile_loaded": False,
                "last_calibration_id": "n/a",
                "attention_low_threshold": "n/a",
                "attention_high_threshold": "n/a",
                "preferred_game_id": "n/a",
                "difficulty_level": "n/a",
            },
        }

    def invoke_action(self, action_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        alias_map = {
            "report.list_sessions": "report.list",
            "report.show_session": "report.show",
            "report.export": "report.export_txt",
            "user.load_current": "user.load_current",
        }
        action_id = alias_map.get(action_id, action_id)
        self.last_command = {"command": action_id, "args": deepcopy(payload), "type": "action_id"}
        self.command_count += 1
        map_cmd = {
            "app.refresh_now": "refresh_snapshot",
            "live.reconnect": "refresh_snapshot",
            "live.safe_stop": "end_session",
            "user.load_current": "load_demo_user",
            "user.ensure_demo_debug": "load_demo_user",
            "session.start": "start_training_session" if self.mode == "live-control" else "start_mock_session",
            "session.stop": "end_training_session" if self.mode == "live-control" else "end_session",
            "diagnostics.refresh": "refresh_snapshot",
        }

        result: dict[str, Any]
        if action_id == "app.quit":
            result = {"action_id": action_id, "status": "accepted", "result": "quit_requested", "accepted": True}
        elif action_id == "user.show_profile":
            app = self.get_app_state()
            raw_user_id = payload.get("user_id") if "user_id" in payload else (self._current_user_override or app.get("current_user_id"))
            user_id = str(raw_user_id or "").strip()
            if not user_id:
                result = {"action_id": action_id, "status": "missing_user", "result": "missing_user", "message": "missing_user", "accepted": False}
            else:
                ps = self._fetch_profile_summary(user_id)
                cs = self._fetch_calibration_status(user_id)
                detail = dict(ps)
                detail.update({
                    "calibration_status": cs.get("calibration_status", cs.get("status", "n/a")),
                    "calibration_usable": cs.get("calibration_usable", "n/a"),
                    "latest_valid": cs.get("latest_valid", "n/a"),
                    "attention_baseline": cs.get("attention_baseline", "n/a"),
                    "gyro_noise_rms": cs.get("gyro_noise_rms", "n/a"),
                    "calibration_failure_reason": cs.get("failure_reason", ""),
                })
                result = {
                    "action_id": action_id,
                    "status": ps.get("status", "profile_not_available"),
                    "result": "profile",
                    "message": ps.get("message", ""),
                    "accepted": ps.get("status") == "accepted",
                    "user_id": user_id,
                    "detail": detail,
                    "profile": ps,
                    "calibration": cs,
                }
        elif action_id == "calibration.status":
            app = self.get_app_state()
            raw_user_id = payload.get("user_id") if "user_id" in payload else (self._current_user_override or app.get("current_user_id"))
            user_id = str(raw_user_id or "").strip()
            if not user_id:
                result = {"action_id": action_id, "status": "missing_user", "result": "missing_user", "message": "missing_user", "accepted": False, "calibration": {"calibration_status": "missing_user"}}
            else:
                cs = self._fetch_calibration_status(user_id)
                result = {"action_id": action_id, "status": cs.get("status", "no_calibration"), "result": "calibration_status", "message": cs.get("message", cs.get("status", "")), "accepted": cs.get("status") == "accepted", "calibration": cs, "detail": cs, "user_id": user_id}
        elif action_id == "session.status":
            result = {"action_id": action_id, "status": "accepted", "result": "session_status", "accepted": True, "session": self.get_session_state()}
        elif action_id == "game.select":
            game_id = str(payload.get("game_id") or "").strip()
            summary = self._select_game_summary(game_id)
            result = {
                "action_id": action_id,
                "status": summary.get("status", "unknown"),
                "result": "game_selected" if summary.get("status") == "accepted" else summary.get("status", "unknown"),
                "message": summary.get("message", ""),
                "accepted": bool(summary.get("accepted", False)),
                "game_id": summary.get("game_id", game_id),
                "previous_game_id": summary.get("previous_game_id", ""),
                "game_hud": summary.get("game_hud", self.get_game_hud()),
                "detail": summary,
            }
        elif action_id == "game.difficulty":
            raw_mode = payload.get("mode", payload.get("difficulty_mode", payload.get("debug_difficulty", payload.get("selected_difficulty_mode"))))
            raw_level = payload.get(
                "level",
                payload.get("difficulty_level", payload.get("debug_difficulty", payload.get("selected_difficulty_level"))),
            )
            summary = self._set_game_difficulty_summary(
                str(payload.get("game_id") or ""),
                raw_mode,
                raw_level,
            )
            result = {
                "action_id": action_id,
                "status": summary.get("status", "unknown"),
                "result": "difficulty_updated" if summary.get("status") == "accepted" else summary.get("status", "unknown"),
                "message": summary.get("message", ""),
                "accepted": bool(summary.get("accepted", False)),
                "game_id": summary.get("game_id", "trace_lock"),
                "difficulty_mode": summary.get("difficulty_mode", ""),
                "debug_difficulty": summary.get("debug_difficulty", ""),
                "level": summary.get("level", ""),
                "game_hud": summary.get("game_hud", self.get_game_hud()),
                "detail": summary,
            }
        elif action_id == "game.status":
            result = {"action_id": action_id, "status": "accepted", "result": "game_status", "accepted": True, "game_hud": self.get_game_hud()}
        elif action_id == "user.load_current":
            uid = str(payload.get("user_id") or self.get_app_state().get("current_user_id") or "")
            if not uid:
                result = {"action_id": action_id, "status": "missing_user", "result": "missing_user", "message": "missing_user", "accepted": False}
            else:
                s = self._load_user_summary(uid)
                result = {
                    "action_id": action_id,
                    "status": s.get("status", "user_loaded"),
                    "result": s,
                    "message": s.get("message", "user_loaded"),
                    "accepted": s.get("status") == "user_loaded",
                    "user_id": uid,
                    "detail": s.get("profile", s),
                }
        elif action_id == "diagnostics.clear_last_error":
            self._last_command_error = ""
            result = {"action_id": action_id, "status": "accepted", "result": "cleared", "accepted": True}
        elif action_id == "calibration.start":
            # Keep the TASK23A/TASK23B contract boundary: only live-control may start
            # the real calibration process. Readonly/core modes still expose operator
            # guidance and a visible progress state so the desktop calibration card can
            # explain what is blocking the run.
            if self.mode in {"core", "core-control", "live-readonly"}:
                app = self.get_app_state()
                raw_user_id = payload.get("user_id") if "user_id" in payload else (self._current_user_override or app.get("current_user_id"))
                user_id = str(raw_user_id or "").strip()
                self._set_current_user_context(user_id)
                self._calibration_user_id = user_id
                self._calibration_started_at_ms = int(time.time() * 1000)
                self._calibration_exit_code = None
                self._calibration_current_phase = "phase 1/4"
                self._calibration_output_lines = [
                    "[gui] Calibration start requested from desktop card.",
                    "[gui] Real calibration requires live-control mode and a connected device.",
                ] + self._format_calibration_phase_prompts().splitlines()
                progress = self._calibration_progress_summary()
                result = {
                    "action_id": action_id,
                    "status": "live_control_required",
                    "result": "calibration_progress",
                    "message": "calibration_start_requires_live_control",
                    "accepted": False,
                    "user_id": user_id,
                    "progress": progress,
                    "detail": progress,
                }
            else:
                app = self.get_app_state()
                raw_user_id = payload.get("user_id") if "user_id" in payload else (self._current_user_override or app.get("current_user_id"))
                user_id = str(raw_user_id or "").strip()
                self._set_current_user_context(user_id)
                summary = self._start_calibration_summary(user_id, payload)
                status = summary.get("status", "started")
                result = {
                    "action_id": action_id,
                    "status": status,
                    "result": "calibration_progress",
                    "message": summary.get("message", status),
                    "accepted": status in {"started", "already_running", "start_guidance"},
                    "user_id": user_id,
                    "progress": summary.get("progress", {}),
                    "detail": summary,
                }
        elif action_id == "calibration.poll":
            progress = self._calibration_progress_summary()
            result = {
                "action_id": action_id,
                "status": progress.get("status", "idle"),
                "result": "calibration_progress",
                "message": "calibration_progress",
                "accepted": True,
                "user_id": progress.get("user_id", ""),
                "progress": progress,
                "detail": progress,
            }
        elif action_id == "user.list":
            s = self._list_users_summary()
            result = {
                "action_id": action_id,
                "status": s.get("status", "accepted"),
                "result": s,
                "message": s.get("message", "user_list"),
                "accepted": True,
                "items": s.get("items", []),
                "items_count": s.get("items_count", s.get("user_count", 0)),
                "detail": {"user_count": s.get("user_count", 0)},
            }
        elif action_id == "user.create":
            uid = str(payload.get("user_id") or "").strip()
            display_name = str(payload.get("display_name") or uid or "").strip()
            s = self._create_user_summary(uid, display_name)
            accepted = s.get("status") in {"created", "accepted"}
            detail = self._fetch_profile_summary(uid) if accepted and uid else s
            result = {
                "action_id": action_id,
                "status": s.get("status", "unknown"),
                "result": s,
                "message": s.get("message", ""),
                "accepted": accepted,
                "user_id": uid,
                "detail": detail,
            }
        elif action_id == "user.load":
            uid = str(payload.get("user_id") or "").strip()
            if not uid:
                result = {"action_id": action_id, "status": "missing_input", "result": "missing_user_id", "message": "missing_user_id", "accepted": False}
            else:
                s = self._load_user_summary(uid)
                result = {
                    "action_id": action_id,
                    "status": s.get("status", "user_loaded"),
                    "result": s,
                    "message": s.get("message", "user_loaded"),
                    "accepted": s.get("status") == "user_loaded",
                    "user_id": uid,
                    "detail": s.get("profile", s),
                }
        elif action_id in {"calibration.list", "calibration.latest", "calibration.show", "calibration.bind", "calibration.cancel"}:
            app = self.get_app_state()
            # A payload that explicitly provides user_id must be respected even when it is blank.
            # This keeps validation predictable: {"user_id": ""} means missing_user instead of
            # silently falling back to the current mock/live user.
            raw_user_id = payload.get("user_id") if "user_id" in payload else (self._current_user_override or app.get("current_user_id"))
            user_id = str(raw_user_id or "").strip()
            calibration_id = str(payload.get("calibration_id") or "").strip()
            if not user_id and action_id != "calibration.show":
                result = {"action_id": action_id, "status": "missing_user", "result": "missing_user", "message": "missing_user", "accepted": False, "items": [], "items_count": 0}
            elif action_id == "calibration.list":
                summary = self._fetch_calibration_list(user_id)
                result = {"action_id": action_id, "status": summary.get("status", "accepted"), "result": summary, "message": summary.get("message", "calibration_list"), "accepted": summary.get("status") == "accepted", "items": summary.get("items", []), "items_count": summary.get("items_count", summary.get("calibration_count", 0)), "calibrations": summary.get("calibrations", []), "user_id": user_id}
            elif action_id == "calibration.latest":
                summary = self._fetch_latest_calibration(user_id)
                result = {"action_id": action_id, "status": summary.get("status", "no_calibration"), "result": summary, "message": summary.get("message", "latest_calibration"), "accepted": summary.get("status") == "accepted", "detail": summary, "calibration": summary, "user_id": user_id}
            elif action_id == "calibration.show":
                if not calibration_id:
                    result = {"action_id": action_id, "status": "missing_input", "result": "missing_calibration_id", "message": "missing_calibration_id", "accepted": False, "user_id": user_id}
                else:
                    summary = self._fetch_calibration_detail(calibration_id)
                    detail_user_id = str(summary.get("user_id") or "").strip() if isinstance(summary, dict) else ""
                    if summary.get("status") == "accepted" and user_id and detail_user_id and detail_user_id != user_id:
                        summary = {
                            "status": "calibration_user_mismatch",
                            "message": "calibration_user_mismatch",
                            "user_id": user_id,
                            "calibration_id": calibration_id,
                            "calibration_user_id": detail_user_id,
                            "detail": summary,
                        }
                    result = {"action_id": action_id, "status": summary.get("status", "calibration_not_found"), "result": summary, "message": summary.get("message", "calibration_detail"), "accepted": summary.get("status") == "accepted", "detail": summary.get("detail", summary) if isinstance(summary, dict) else summary, "calibration": summary, "user_id": user_id, "calibration_id": calibration_id}
            elif action_id == "calibration.bind":
                summary = self._bind_calibration_summary(user_id, calibration_id)
                result = {"action_id": action_id, "status": summary.get("status", "unknown"), "result": summary, "message": summary.get("message", ""), "accepted": summary.get("status") == "accepted", "detail": summary.get("detail", summary), "calibration": summary.get("calibration", {}), "user_id": user_id, "calibration_id": calibration_id}
            else:
                summary = self._cancel_calibration_summary(user_id)
                result = {"action_id": action_id, "status": summary.get("status", "cancelled"), "result": summary, "message": summary.get("message", "cancelled_by_user"), "accepted": summary.get("status") == "cancelled", "detail": summary, "progress": summary.get("progress", self._calibration_progress_summary()), "user_id": user_id}
        elif action_id in {"report.refresh", "report.latest", "report.list", "report.show", "report.export_txt"}:
            app = self.get_app_state()
            raw_user_id = payload.get("user_id") if "user_id" in payload else (self._current_user_override or app.get("current_user_id"))
            user_id = str(raw_user_id or "").strip()
            if action_id == "report.refresh":
                summary = self._refresh_report_summary(user_id)
                result = {
                    "action_id": action_id,
                    "status": summary.get("status", "accepted"),
                    "result": summary,
                    "message": summary.get("message", "report_refreshed"),
                    "accepted": summary.get("status") in {"accepted", "no_report_available"},
                    "detail": summary.get("detail", summary),
                    "report": summary.get("report", summary.get("detail", summary)),
                    "user_id": user_id,
                    "session_id": summary.get("latest_session_id", summary.get("session_id", "")),
                    "report_path": summary.get("latest_report_path", summary.get("report_path", "")),
                    "latest_report_path": summary.get("latest_report_path", summary.get("report_path", "")),
                    "report_preview": summary.get("report_preview", ""),
                }
            elif action_id == "report.latest":
                summary = self._fetch_latest_report_summary(user_id)
                result = {
                    "action_id": action_id,
                    "status": summary.get("status", "no_report_available"),
                    "result": summary,
                    "message": summary.get("message", "latest_report"),
                    "accepted": summary.get("status") == "accepted",
                    "detail": summary.get("detail", summary),
                    "report": summary.get("report", summary.get("detail", summary)),
                    "user_id": user_id,
                    "session_id": summary.get("latest_session_id", ""),
                    "report_path": summary.get("latest_report_path", ""),
                    "latest_report_path": summary.get("latest_report_path", ""),
                    "report_preview": summary.get("report_preview", ""),
                }
            elif action_id == "report.list":
                summary = self._fetch_report_session_list(user_id)
                list_items = summary.get("items", [])
                list_sessions = summary.get("sessions", [])
                list_text = summary.get("report_list_text", "")
                list_count = summary.get("items_count", summary.get("session_count", 0))
                # Keep report.list action payload lightweight.  The QML card only needs
                # compact items and report_list_text; duplicating the same list under
                # result/detail/report made raw JSON very large and caused visible lag.
                result = {
                    "action_id": action_id,
                    "status": summary.get("status", "accepted"),
                    "result": {
                        "status": summary.get("status", "accepted"),
                        "message": summary.get("message", "report_list"),
                        "user_id": user_id,
                        "items_count": list_count,
                        "session_count": list_count,
                        "report_list_text": list_text,
                    },
                    "message": summary.get("message", "report_list"),
                    "accepted": True,
                    "items": list_items,
                    "items_count": list_count,
                    "sessions": list_sessions,
                    "report_list_text": list_text,
                    "user_id": user_id,
                    "detail": {"items_count": list_count, "report_list_text": list_text},
                    "report": {"items_count": list_count, "report_list_text": list_text},
                }
            elif action_id == "report.show":
                report_identifier = str(payload.get("report_id") or payload.get("session_id") or "").strip()
                report_path = str(payload.get("report_path") or "").strip()
                file_index = payload.get("file_index")
                if report_identifier.isdigit() and not report_path and file_index in (None, "", "n/a"):
                    file_index = report_identifier
                    report_identifier = ""
                detail = self._fetch_report_session_detail(session_id=report_identifier, user_id=user_id, report_path=report_path, file_index=file_index)
                if bool(payload.get("allow_latest_fallback", False)) and not report_path and (detail.get("status") != "accepted" or not self._report_item_has_readable_report(detail)):
                    latest = self._fetch_latest_report_summary(user_id)
                    latest_detail = latest.get("detail") if isinstance(latest.get("detail"), dict) else {}
                    if latest.get("status") == "accepted" and latest_detail:
                        detail = dict(latest_detail)
                        detail["status"] = "accepted"
                        detail["message"] = "latest_report_fallback_loaded"
                result = {
                    "action_id": action_id,
                    "status": detail.get("status", "session_not_found"),
                    "result": detail,
                    "message": detail.get("message", ""),
                    "accepted": detail.get("status") == "accepted",
                    "detail": detail,
                    "report": detail,
                    "user_id": user_id,
                    "session_id": detail.get("session_id", report_identifier),
                    "report_path": detail.get("report_path", report_path),
                    "report_preview": detail.get("report_preview", ""),
                }
            else:
                report_identifier = str(payload.get("report_id") or payload.get("session_id") or "").strip()
                report_path = str(payload.get("report_path") or "").strip()
                file_index = payload.get("file_index")
                if report_identifier.isdigit() and not report_path and file_index in (None, "", "n/a"):
                    file_index = report_identifier
                    report_identifier = ""
                summary = self._export_report_txt(user_id=user_id, session_id=report_identifier, report_path=report_path, file_index=file_index, out_dir=str(payload.get("out_dir") or "reports/exports"), allow_latest_fallback=bool(payload.get("allow_latest_fallback", False)))
                result = {
                    "action_id": action_id,
                    "status": summary.get("status", "export_failed"),
                    "result": summary,
                    "message": summary.get("message", ""),
                    "accepted": summary.get("status") == "accepted",
                    "detail": summary.get("detail", summary),
                    "report": summary.get("report", summary.get("detail", summary)),
                    "user_id": user_id,
                    "session_id": summary.get("session_id", report_identifier),
                    "report_path": summary.get("source_report_path", report_path),
                    "source_report_path": summary.get("source_report_path", report_path),
                    "export_path": summary.get("export_path", ""),
                    "report_preview": (summary.get("detail") or {}).get("report_preview", "") if isinstance(summary.get("detail"), dict) else "",
                }
        elif action_id == "devlab.run":
            result = {"action_id": action_id, "status": "not_implemented_in_this_task", "result": payload, "message": "manual_or_copy_only", "accepted": False}
        else:
            cmd = map_cmd.get(action_id)
            if not cmd:
                result = {"action_id": action_id, "status": "unsupported", "result": "unsupported", "accepted": False}
            elif self.mode in {"core", "live-readonly"} and action_id in {"live.safe_stop", "user.ensure_demo_debug", "session.start", "session.stop"}:
                result = {"action_id": action_id, "status": "readonly_not_allowed", "result": "readonly_not_allowed", "accepted": False}
            elif action_id == "live.safe_stop" and self.mode != "live-control":
                result = {"action_id": action_id, "status": "unsupported", "result": "unsupported", "accepted": False, "reason": "live_control_required"}
            else:
                payload = dict(payload)
                if action_id in {"session.start", "user.ensure_demo_debug", "user.load_current"} and "user_id" not in payload:
                    payload["user_id"] = self._current_user_override or self.get_app_state().get("current_user_id") or payload.get("user_id")
                if action_id == "session.start":
                    requested_game_id = str(payload.get("game_id") or self.get_app_state().get("current_game_id") or "trace_lock").strip()
                    if requested_game_id:
                        select_result = self._select_game_summary(requested_game_id)
                        if select_result.get("status") not in {"accepted", "not_implemented"} and self.mode == "live-control":
                            self.last_command_result = {
                                "action_id": action_id,
                                "status": select_result.get("status", "game_select_failed"),
                                "result": select_result,
                                "message": select_result.get("message", "game_select_failed"),
                                "accepted": False,
                            }
                            result = deepcopy(self.last_command_result)
                            self._last_command_error = str(result.get("status") or "")
                            print(f"[GUI ACTION] action_id={action_id} status={result.get('status')} result={self._action_log_summary(result)} message='{result.get('message', '')}'", flush=True)
                            return result
                self.handle_gui_command(cmd, payload)
                status = self.last_command_result.get("status", "unknown") if isinstance(self.last_command_result, dict) else "unknown"
                result = {"action_id": action_id, "status": status, "result": self.last_command_result, "accepted": bool(self.last_command_result.get("accepted", False)) if isinstance(self.last_command_result, dict) else False}

        if action_id == "session.start" and str(result.get("status")) in {"training_started", "live_debug_started", "completed"}:
            if not self._active_session_started_at_ms:
                self._active_session_started_at_ms = int(time.time() * 1000)
        if action_id in {"session.stop", "live.safe_stop"} and str(result.get("status")) in {"training_completed", "training_stopped", "live_debug_stopped", "noop"}:
            self._active_session_started_at_ms = None

        self.last_command_result = deepcopy(result)
        status = str(result.get("status") or "")
        self._last_command_error = "" if status in {"accepted", "completed", "training_started", "training_completed", "live_debug_started", "live_debug_stopped", "noop"} else status
        print(
            f"[GUI ACTION] action_id={action_id} status={status} result={self._action_log_summary(result)} message='{result.get('message', result.get('reason', ''))}'",
            flush=True,
        )
        return result
