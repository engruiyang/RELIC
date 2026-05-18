from __future__ import annotations

from copy import deepcopy
import sqlite3
import subprocess
import sys
import threading
import time
from typing import Any

from .gui_core_source import GuiCoreSnapshotSource
from .gui_live_readonly_source import GuiLiveReadonlySource
from .gui_live_control_source import GuiLiveControlSource
from core.resource_managers import build_render_resource_bundle
from storage.sqlite_store import SqliteStore
from .command_registry import build_page_command_manifest


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
                self.last_command_result = self._live_control_source.start_training_session(args.get("user_id"), args.get("db_path", self.db_path))
            elif command == "end_training_session":
                self.last_command_result = self._live_control_source.end_training_session()
            elif command == "end_session":
                self.last_command_result = self._live_control_source.end_training_session() if self._live_control_source.session_type == "training" else self._live_control_source.end_live_debug_session()
            elif command == "set_debug_difficulty":
                self.last_command_result = self._live_control_source.set_debug_difficulty(args.get("level"))
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

    def get_render_resources(self) -> dict[str, Any]:
        return deepcopy(self._render_resources)


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
            return {"status": "accepted", "message": "profile_loaded", "current_user_id": user_id, "user_type": user.get("user_type", "local_user"), "profile_loaded": True, "last_calibration_id": profile.get("last_calibration_id") or "n/a", "attention_low_threshold": profile.get("attention_low_threshold", "n/a"), "attention_high_threshold": profile.get("attention_high_threshold", "n/a"), "preferred_game_id": profile.get("preferred_game_id", "n/a"), "difficulty_level": profile.get("difficulty_level", "n/a")}
        finally:
            store.close()

    def _fetch_calibration_status(self, user_id: str) -> dict[str, Any]:
        store = SqliteStore(self.db_path)
        store.connect()
        try:
            profile = store.get_user_profile(user_id)
            if not profile:
                return {"status": "profile_without_calibration", "calibration_status": "profile_without_calibration", "last_calibration_id": "n/a", "calibration_usable": False, "latest_valid": False, "failure_reason": "profile_not_found", "source": "profile"}
            cal_id = profile.get("last_calibration_id")
            if not cal_id:
                return {"status": "no_calibration", "calibration_status": "no_calibration", "last_calibration_id": "n/a", "calibration_usable": False, "latest_valid": False, "failure_reason": "no_calibration", "source": "profile"}
            cp = store.get_calibration_profile(str(cal_id))
            if not cp:
                return {"status": "no_calibration", "calibration_status": "no_calibration", "last_calibration_id": cal_id, "calibration_usable": False, "latest_valid": False, "failure_reason": "calibration_id_not_found", "source": "profile"}
            return {"status": "accepted", "calibration_status": "available", "last_calibration_id": cal_id, "calibration_usable": bool(cp.get("valid")), "latest_valid": bool(cp.get("valid")), "failure_reason": cp.get("failure_reason") or "", "source": cp.get("calibration_type") or "calibration_profile", "attention_baseline": cp.get("attention_baseline") if cp.get("attention_baseline") is not None else "n/a", "gyro_noise_rms": cp.get("gyro_noise_rms") if cp.get("gyro_noise_rms") is not None else "n/a"}
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
            return {"status": "missing_user", "message": "missing_user", "items": [], "items_count": 0}
        conn = self._connect_readonly_db()
        try:
            table_name = self._calibration_table_name(conn)
            if not table_name:
                return {"status": "accepted", "message": "no_calibration_table", "items": [], "items_count": 0, "calibrations": []}
            columns = self._table_columns(conn, table_name)
            order_sql = " ORDER BY created_at DESC" if "created_at" in columns else " ORDER BY rowid DESC"
            if "user_id" in columns:
                rows = conn.execute(f"SELECT * FROM {table_name} WHERE user_id=?" + order_sql, (user_id,)).fetchall()
            else:
                rows = conn.execute(f"SELECT * FROM {table_name}" + order_sql).fetchall()
            items = [self._normalize_calibration_record(dict(row)) for row in rows]
            if not items:
                status = self._fetch_calibration_status(user_id)
                bound_id = status.get("last_calibration_id")
                if bound_id and bound_id != "n/a":
                    detail = self._fetch_calibration_detail(str(bound_id))
                    if detail.get("status") == "accepted":
                        items.append(detail)
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
        return {"status": "cancelled", "message": "cancelled_by_user", "user_id": user_id, "valid": False, "failure_reason": "cancelled_by_user"}



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

        running = process is not None and process.poll() is None
        if running:
            status = "running"
        elif self._calibration_exit_code is None and self._calibration_started_at_ms is None:
            status = "idle"
        elif self._calibration_exit_code == 0:
            status = "completed"
        else:
            status = "failed"

        output_tail = self._calibration_output_lines[-120:]
        phase_lines = [line for line in output_tail if line.startswith("[phase")]
        if phase_lines:
            self._calibration_current_phase = phase_lines[-1].split("]", 1)[0].strip("[") if "]" in phase_lines[-1] else phase_lines[-1]

        phase_prompt_text = self._format_calibration_phase_prompts()
        output_text = "\n".join(output_tail) if output_tail else "No calibration CLI output yet."
        current_phase = self._calibration_current_phase or ("phase 1/4" if running else "n/a")
        current_phase_detail = self._current_calibration_phase_detail()
        return {
            "status": status,
            "running": running,
            "user_id": self._calibration_user_id,
            "started_at_ms": self._calibration_started_at_ms,
            "exit_code": self._calibration_exit_code,
            "current_phase": current_phase,
            "current_phase_detail": current_phase_detail,
            "phase_prompts": self._calibration_phase_prompts(),
            "phase_prompt_text": phase_prompt_text,
            "output_count": len(self._calibration_output_lines),
            "output_tail": output_tail,
            "output_text": output_text,
            "operator_guidance": phase_prompt_text,
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

        calibration_type = str(payload.get("calibration_type") or "auto").strip() or "auto"
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
            item("diagnostics.clear_last_error", "Clear Last Error", "diagnostics", True, True, False, "clear last command error"),
            item("diagnostics.refresh", "Refresh Diagnostics", "diagnostics", True, True, False, "refresh diagnostics")
        ]

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
        return {
            "mode": self.mode,
            "control_enabled": self.mode != "core",
            "readonly": self.mode in {"core", "live-readonly"},
            "current_user_id": app.get("current_user_id", ""),
            "current_session_id": session.get("session_id", "") or ("session_id_unavailable" if session_active else ""),
            "current_game_id": app.get("current_game_id", session.get("game_id", "")),
            "session_active": session_active,
            "calibration_active": False,
            "live_connected": app.get("connection_status") == "connected" or app.get("source") in {"live_readonly", "live_control"},
            "last_command": self.last_command.get("command", "") if isinstance(self.last_command, dict) else "",
            "last_command_result": self.last_command_result.get("status", "") if isinstance(self.last_command_result, dict) else "",
            "last_command_error": self._last_command_error,
            "command_count": self.command_count,
            "latest_report_path": session.get("latest_report_path") or session.get("report_path") or "",
            "app_elapsed_ms": now - self._started_at_ms,
            "session_elapsed_ms": session_elapsed_ms if session_active else "n/a",
            "last_session_status": session.get("training_status", "none"),
            "profile_status": self.last_command_result.get("status", "") if isinstance(self.last_command_result, dict) and self.last_command.get("command") == "user.show_profile" else "",
            "user_type": self.last_command_result.get("profile", {}).get("user_type", "") if isinstance(self.last_command_result, dict) else "",
            "profile_loaded": self.last_command_result.get("profile", {}).get("profile_loaded", "") if isinstance(self.last_command_result, dict) else "",
            "last_calibration_id": self.last_command_result.get("calibration", {}).get("last_calibration_id", self.last_command_result.get("profile", {}).get("last_calibration_id", "n/a")) if isinstance(self.last_command_result, dict) else "n/a",
            "calibration_status": self.last_command_result.get("calibration", {}).get("calibration_status", "") if isinstance(self.last_command_result, dict) else "",
            "calibration_usable": self.last_command_result.get("calibration", {}).get("calibration_usable", "") if isinstance(self.last_command_result, dict) else "",
        }

    def _set_current_user_context(self, user_id: str, display_name: str | None = None, user_type: str = "local_user") -> None:
        if not user_id:
            return
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
            user_id = str(payload.get("user_id") or app.get("current_user_id") or "").strip()
            if not user_id:
                result = {"action_id": action_id, "status": "missing_user", "result": "missing_user", "message": "missing_user", "accepted": False}
            else:
                ps = self._fetch_profile_summary(user_id)
                result = {"action_id": action_id, "status": ps.get("status", "profile_not_available"), "result": "profile", "message": ps.get("message", ""), "accepted": ps.get("status") == "accepted", "user_id": user_id, "detail": ps, "profile": ps}
        elif action_id == "calibration.status":
            app = self.get_app_state()
            user_id = str(payload.get("user_id") or app.get("current_user_id") or "").strip()
            if not user_id:
                result = {"action_id": action_id, "status": "missing_user", "result": "missing_user", "message": "missing_user", "accepted": False, "calibration": {"calibration_status": "missing_user"}}
            else:
                cs = self._fetch_calibration_status(user_id)
                result = {"action_id": action_id, "status": cs.get("status", "no_calibration"), "result": "calibration_status", "message": cs.get("message", cs.get("status", "")), "accepted": cs.get("status") == "accepted", "calibration": cs, "detail": cs, "user_id": user_id}
        elif action_id == "session.status":
            result = {"action_id": action_id, "status": "accepted", "result": "session_status", "accepted": True, "session": self.get_session_state()}
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
            # the real calibration process. Readonly/core modes still report the
            # workflow as not implemented, while mock keeps deterministic progress
            # guidance for GUI tests and page preview.
            if self.mode in {"core", "core-control", "live-readonly"}:
                result = {
                    "action_id": action_id,
                    "status": "not_implemented",
                    "result": "not_implemented",
                    "message": "calibration_start_requires_live_control",
                    "accepted": False,
                    "progress": self._calibration_progress_summary(),
                }
            else:
                app = self.get_app_state()
                raw_user_id = payload.get("user_id") if "user_id" in payload else app.get("current_user_id")
                user_id = str(raw_user_id or "").strip()
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
            raw_user_id = payload.get("user_id") if "user_id" in payload else app.get("current_user_id")
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
                    result = {"action_id": action_id, "status": summary.get("status", "calibration_not_found"), "result": summary, "message": summary.get("message", "calibration_detail"), "accepted": summary.get("status") == "accepted", "detail": summary, "calibration": summary, "user_id": user_id, "calibration_id": calibration_id}
            elif action_id == "calibration.bind":
                summary = self._bind_calibration_summary(user_id, calibration_id)
                result = {"action_id": action_id, "status": summary.get("status", "unknown"), "result": summary, "message": summary.get("message", ""), "accepted": summary.get("status") == "accepted", "detail": summary.get("detail", summary), "calibration": summary.get("calibration", {}), "user_id": user_id, "calibration_id": calibration_id}
            else:
                summary = self._cancel_calibration_summary(user_id)
                result = {"action_id": action_id, "status": summary.get("status", "cancelled"), "result": summary, "message": summary.get("message", "cancelled_by_user"), "accepted": summary.get("status") == "cancelled", "detail": summary, "user_id": user_id}
        elif action_id == "report.refresh":
            result = {"action_id": action_id, "status": "accepted", "result": self.get_session_state(), "message": "report_refreshed", "accepted": True}
        elif action_id in {"report.list", "report.show", "report.export"}:
            result = {"action_id": action_id, "status": "unsupported_in_current_mode", "result": "unsupported_in_current_mode", "accepted": False}
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
                    payload["user_id"] = self.get_app_state().get("current_user_id") or payload.get("user_id")
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
        return result
