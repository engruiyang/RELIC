from __future__ import annotations

import threading
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from storage.sqlite_store import SqliteStore
from storage.session_report_writer import write_session_report

from game.game_client_registry import create_game_client
from game.game_contracts import GameInputEvent
from .game_event_platform_adapter import GameEventPlatformAdapter
from .gui_live_readonly_source import GuiLiveReadonlySource


class GuiLiveControlSource:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000, poll_interval_sec: float = 0.1, live_source: GuiLiveReadonlySource | None = None, user_id: str = "demo_user", game_id: str = "fake_game") -> None:
        self.user_id = user_id
        self.game_id = game_id
        self.poll_interval_sec = poll_interval_sec
        self._live_source = live_source or GuiLiveReadonlySource(host=host, port=port, poll_interval_sec=poll_interval_sec)
        self._client = create_game_client(game_id)
        self._platform_adapter = GameEventPlatformAdapter()
        self._lock = threading.Lock()
        self._tick_thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._event_seq = 0

        self.live_debug_session_id: str | None = None
        self.training_session_id: str | None = None
        self.session_type: str = ""
        self.interaction_enabled = False
        self.session_type = ""
        self._store = SqliteStore("data/relic_local.db")
        self._training_context: dict[str, Any] = {}
        self._training_samples: list[dict[str, Any]] = []
        self._training_runtime: list[dict[str, Any]] = []
        self.game_update_count = 0
        self.last_runtime_attention: int | None = None
        self.last_runtime_attention_fresh = False
        self.last_runtime_gyro_fresh = False
        self.last_game_event: dict[str, Any] = {}
        self.last_game_action_name = ""
        self.last_game_target_index: int | None = None
        self.game_event_count = 0
        self.last_game_view: dict[str, Any] = asdict(self._client.build_game_view())
        self.last_report_path = ""
        self.last_training_status = "idle"
        self.last_session_id = ""

    def start(self) -> None:
        self._live_source.start()
        self._stop.clear()
        self._tick_thread = threading.Thread(target=self._tick_loop, daemon=True, name="GuiLiveControlTick")
        self._tick_thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._tick_thread and self._tick_thread.is_alive():
            self._tick_thread.join(timeout=1.0)
        self._live_source.stop()

    def _tick_loop(self) -> None:
        while not self._stop.is_set():
            runtime = self._live_source.get_runtime_snapshot()
            self._client.update(runtime, int(self.poll_interval_sec * 1000))
            self._drain_game_events()
            view = self._client.build_game_view()
            with self._lock:
                self.game_update_count += 1
                self.last_runtime_attention = runtime.get("attention")
                self.last_runtime_attention_fresh = bool(runtime.get("attention_fresh"))
                self.last_runtime_gyro_fresh = bool(runtime.get("gyro_fresh"))
                self.last_game_view = asdict(view)
                if self.interaction_enabled and self.session_type == "training":
                    self._training_runtime.append({"fi": runtime.get("fi") if runtime.get("fi") is not None else runtime.get("focus_index"), "sqi": runtime.get("sqi"), "control_state": runtime.get("control_state"), "quality_state": runtime.get("quality_state"), "warning_flags": list(runtime.get("warning_flags") or []), "error_flags": list(runtime.get("error_flags") or [])})
            time.sleep(self.poll_interval_sec)

    def _drain_game_events(self) -> None:
        events = self._client.collect_game_events()
        for evt in events:
            evt_dict = evt.to_dict()
            self.last_game_event = evt_dict
            self.game_event_count += 1
            ep = evt.payload or {}
            self.last_game_action_name = str(ep.get("action_name") or "")
            ti = ep.get("target_index")
            self.last_game_target_index = ti if isinstance(ti, int) else None
            if not evt.reportable:
                continue
            self._platform_adapter.process_game_event(evt_dict, allow_mock=True)


    def _reset_training_buffers(self) -> None:
        self._training_samples = []
        self._training_runtime = []

    def start_training_session(self, user_id: str | None = None, db_path: str = "data/relic_local.db") -> dict[str, Any]:
        if self.interaction_enabled:
            return {"command": "start_training_session", "accepted": False, "status": "conflict", "message": "active_session_exists", "result": "conflict", "source": "live_control"}
        uid = str(user_id or self.user_id)
        self.user_id = uid
        now = datetime.now(timezone.utc)
        sid = f"training_{uid}_{now.strftime('%Y%m%d_%H%M%S')}"
        self.training_session_id = sid
        self.session_type = "training"
        self.last_training_status = "training_started"
        self.last_session_id = sid
        self._store = SqliteStore(db_path); self._store.connect()
        profile = self._store.get_user_profile(uid)
        calib = self._store.get_latest_calibration_profile(uid)
        self._training_context = {"session_id": sid, "session_type": "training", "user_id": uid, "game_id": self.game_id, "started_at_ms": int(time.time()*1000), "db_path": db_path, "profile_status": "ok" if profile else "missing", "calibration_status": "ok" if calib else "missing", "calibration_fallback": calib is None, "runtime_mode": "live-control", "report_path": ""}
        self._reset_training_buffers()
        manifest = getattr(self._client, "manifest", {}) or {}
        default_difficulty = manifest.get("default_difficulty", 1)
        self._client.start({"session_id": sid, "user_id": uid, "game_id": self.game_id, "difficulty": default_difficulty})
        self.interaction_enabled = True
        return {"command":"start_training_session","accepted":True,"status":"training_started","result":"training_started","session_id":sid,"session_context":dict(self._training_context),"source":"live_control"}

    def end_training_session(self) -> dict[str, Any]:
        if not self.interaction_enabled or not self.training_session_id or self.session_type != "training":
            return {"command":"end_training_session","accepted":True,"status":"training_stopped","result":"noop","message":"no_active_training_session","source":"live_control"}
        self.interaction_enabled = False
        self._client.stop("training_completed")
        self._client.collect_game_events()
        sample = self._client.collect_behavior_sample().to_dict()
        view = self._client.build_game_view()
        now_ms = int(time.time()*1000)
        started = int(self._training_context.get("started_at_ms") or now_ms)
        fi_vals=[float(x.get("fi")) for x in self._training_runtime if x.get("fi") is not None]
        sqi_vals=[float(x.get("sqi")) for x in self._training_runtime if x.get("sqi") is not None]
        summary={"session_id":self.training_session_id,"user_id":self.user_id,"game_id":self.game_id,"started_at":datetime.fromtimestamp(started/1000,tz=timezone.utc).isoformat(),"ended_at":datetime.now(timezone.utc).isoformat(),"status":"training_completed","session_type":"training","score":view.score,"combo":view.combo,"max_combo":view.hud.get("max_combo"),"level_final":view.level,"target_count":sample.get("target_count"),"correct_count":sample.get("correct_count"),"omission_count":sample.get("omission_count"),"false_action_count":sample.get("false_action_count"),"accuracy":sample.get("accuracy"),"omission":sample.get("omission"),"false_action":sample.get("false_action"),"rt_stability":sample.get("rt_stability"),"fi_avg":(sum(fi_vals)/len(fi_vals) if fi_vals else None),"sqi_avg":(sum(sqi_vals)/len(sqi_vals) if sqi_vals else None),"final_fi_avg":(sum(fi_vals)/len(fi_vals) if fi_vals else None),"final_sqi_avg":(sum(sqi_vals)/len(sqi_vals) if sqi_vals else None),"calibration_status":self._training_context.get("calibration_status","missing"),"profile_status":self._training_context.get("profile_status","missing"),"warning_count":sum(len(x.get("warning_flags",[])) for x in self._training_runtime),"error_count":sum(len(x.get("error_flags",[])) for x in self._training_runtime),"total_duration_ms":now_ms-started}
        report_path = write_session_report(summary, {"event_count": len(self._training_samples)}, out_dir="reports/sessions")
        summary["report_path"]=report_path
        self._store.upsert_training_session(summary)
        self.last_game_view = asdict(view)
        self._training_context["report_path"]=report_path
        self.last_report_path = report_path
        self.last_training_status = "training_completed"
        self.last_session_id = str(self.training_session_id or "")
        self.session_type = ""
        return {"command":"end_training_session","accepted":True,"status":"training_completed","result":"training_completed","report_path":report_path,"session_id":self.training_session_id,"source":"live_control"}

    def start_live_debug_session(self, user_id: str | None = None) -> dict[str, Any]:
        if self.interaction_enabled and self.session_type == "training":
            return {"command": "start_mock_session", "accepted": False, "status": "conflict", "message": "active_training_session", "result": "conflict", "source": "live_control"}
        uid = str(user_id or self.user_id)
        self.user_id = uid
        sid = f"live_debug_{uid}_{time.strftime('%Y%m%d_%H%M%S')}"
        # avoid same-second reuse
        if sid == self.live_debug_session_id:
            sid = f"{sid}_{int(time.time() * 1000) % 1000:03d}"
        self.live_debug_session_id = sid
        manifest = getattr(self._client, "manifest", {}) or {}
        default_difficulty = manifest.get("default_difficulty", 1)
        self._client.start({"session_id": sid, "user_id": uid, "game_id": self.game_id, "difficulty": default_difficulty})
        self.interaction_enabled = True
        self.session_type = "debug"
        self.last_session_id = sid
        return {"command": "start_mock_session", "accepted": True, "status": "live_debug_started", "message": "live debug session started", "result": "live_debug_started", "session_id": sid, "source": "live_control"}

    def end_live_debug_session(self) -> dict[str, Any]:
        if not self.interaction_enabled or not self.live_debug_session_id:
            return {"command": "end_session", "accepted": True, "status": "noop", "message": "no_active_session", "result": "noop", "source": "live_control"}
        self.interaction_enabled = False
        self.session_type = ""
        self._client.stop("live_debug_stopped")
        self._client.collect_game_events()
        return {"command": "end_session", "accepted": True, "status": "live_debug_stopped", "message": "live debug session stopped", "result": "live_debug_stopped", "source": "live_control"}

    def handle_pointer_click(self, payload: dict[str, Any]) -> dict[str, Any]:
        active_session_id = self.training_session_id if self.session_type == "training" else self.live_debug_session_id
        if not self.interaction_enabled or not active_session_id:
            return {"result": "no_active_live_debug_session", "status": "ignored", "reason": "no_active_live_debug_session", "source": "live_control"}
        self._event_seq += 1
        ge = GameInputEvent(event_id=f"live_ctrl_input_{self._event_seq}", session_id=active_session_id, game_id=self.game_id, input_type="pointer_click", created_at_ms=int(time.time() * 1000), source="minimal_game_canvas", x_norm=float(payload.get("x_norm", 0.0)), y_norm=float(payload.get("y_norm", 0.0)), button=0, raw_event_type="pointer_click", debug_hit=payload.get("hit"), payload=dict(payload))
        print(f"[GAME INPUT] type={ge.input_type} x={ge.x_norm:.3f} y={ge.y_norm:.3f} session_id={ge.session_id}", flush=True)
        self._client.handle_input(ge)
        events = self._client.collect_game_events()
        result = "recorded_only"
        for evt in events:
            evt_dict = evt.to_dict()
            self.last_game_event = evt_dict
            self.game_event_count += 1
            ep = evt.payload or {}
            self.last_game_action_name = str(ep.get("action_name") or "")
            ti = ep.get("target_index")
            self.last_game_target_index = ti if isinstance(ti, int) else None
            print(
                f"[GAME EVENT] event_type={evt.event_type} target_index={ep.get('target_index')} action={ep.get('action_name')} hit={ep.get('hit')}",
                flush=True,
            )
            platform_res = self._platform_adapter.process_game_event(evt_dict, allow_mock=True)
            result = str(platform_res.get("platform_result") or result)
        self.last_game_view = asdict(self._client.build_game_view())
        if self.interaction_enabled and self.session_type == "training":
            self._training_samples.append(self._client.collect_behavior_sample().to_dict())
        return {"result": result, "status": "accepted", "reason": result, "source": "live_control", "game_input": ge.to_dict(), "last_game_event": dict(self.last_game_event), "game_event_count": self.game_event_count, "platform_message_count": self._platform_adapter.platform_message_count, "last_platform_message": dict(self._platform_adapter.last_platform_message), "last_platform_result": self._platform_adapter.last_platform_result}

    def get_runtime_snapshot(self) -> dict[str, Any]:
        rt = self._live_source.get_runtime_snapshot()
        with self._lock:
            rt.update({"source": "live_control", "game_update_count": self.game_update_count, "last_runtime_attention": self.last_runtime_attention, "last_runtime_attention_fresh": self.last_runtime_attention_fresh, "last_runtime_gyro_fresh": self.last_runtime_gyro_fresh, "interaction_enabled": self.interaction_enabled, "live_debug_session_id": self.live_debug_session_id or "", "game_event_count": self.game_event_count})
        return rt

    def get_app_state(self) -> dict[str, Any]:
        base = self._live_source.get_app_state()
        base.update({"source": "live_control", "current_user_id": self.user_id, "current_game_id": self.game_id, "session_active": self.interaction_enabled, "allowed_commands": ["refresh_snapshot", "load_demo_user", "start_mock_session", "start_training_session", "end_training_session", "end_session", "open_last_report", "set_debug_difficulty"]})
        return base

    def get_session_state(self) -> dict[str, Any]:
        sid = (self.training_session_id if self.session_type == "training" else self.live_debug_session_id) or self.last_session_id or ""
        report_path = self._training_context.get("report_path") or self.last_report_path or ""
        return {"session_id": sid, "session_type": self.session_type or "none", "training_status": self.last_training_status, "latest_session_id": self.last_session_id, "latest_report_path": report_path, "user_id": self.user_id, "game_id": self.game_id, "session_active": self.interaction_enabled, "score": self.last_game_view.get("score", 0), "warning_count": 0, "error_count": 0, "log_path": "", "report_path": report_path, "platform_report_status": "mock_only", "source": "live_control"}

    def get_game_view(self) -> dict[str, Any]:
        return dict(self.last_game_view)

    def set_debug_difficulty(self, level: int | None) -> dict[str, Any]:
        if self.game_id != "trace_lock":
            return {"command": "set_debug_difficulty", "accepted": True, "status": "unsupported_game", "message": "unsupported_game", "result": "noop", "source": "live_control"}
        if not hasattr(self._client, "set_debug_difficulty"):
            return {"command": "set_debug_difficulty", "accepted": False, "status": "rejected", "message": "unsupported_client", "result": "rejected", "source": "live_control"}
        self._client.set_debug_difficulty(level)
        self.last_game_view = asdict(self._client.build_game_view())
        if self.interaction_enabled and self.session_type == "training":
            self._training_samples.append(self._client.collect_behavior_sample().to_dict())
        return {"command": "set_debug_difficulty", "accepted": True, "status": "accepted", "message": "debug_difficulty_set", "result": "accepted", "source": "live_control", "level": level}
