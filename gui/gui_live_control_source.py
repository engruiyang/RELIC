from __future__ import annotations

import threading
import time
from dataclasses import asdict
from typing import Any

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
        self.interaction_enabled = False
        self.game_update_count = 0
        self.last_runtime_attention: int | None = None
        self.last_runtime_attention_fresh = False
        self.last_runtime_gyro_fresh = False
        self.last_game_event: dict[str, Any] = {}
        self.last_game_action_name = ""
        self.last_game_target_index: int | None = None
        self.game_event_count = 0
        self.last_game_view: dict[str, Any] = asdict(self._client.build_game_view())

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
            view = self._client.build_game_view()
            with self._lock:
                self.game_update_count += 1
                self.last_runtime_attention = runtime.get("attention")
                self.last_runtime_attention_fresh = bool(runtime.get("attention_fresh"))
                self.last_runtime_gyro_fresh = bool(runtime.get("gyro_fresh"))
                self.last_game_view = asdict(view)
            time.sleep(self.poll_interval_sec)

    def start_live_debug_session(self, user_id: str | None = None) -> dict[str, Any]:
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
        return {"command": "start_mock_session", "accepted": True, "status": "live_debug_started", "message": "live debug session started", "result": "live_debug_started", "session_id": sid, "source": "live_control"}

    def end_live_debug_session(self) -> dict[str, Any]:
        if not self.interaction_enabled or not self.live_debug_session_id:
            return {"command": "end_session", "accepted": True, "status": "noop", "message": "no_active_session", "result": "noop", "source": "live_control"}
        self.interaction_enabled = False
        self._client.stop("live_debug_stopped")
        self._client.collect_game_events()
        return {"command": "end_session", "accepted": True, "status": "live_debug_stopped", "message": "live debug session stopped", "result": "live_debug_stopped", "source": "live_control"}

    def handle_pointer_click(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.interaction_enabled or not self.live_debug_session_id:
            return {"result": "no_active_live_debug_session", "status": "ignored", "reason": "no_active_live_debug_session", "source": "live_control"}
        self._event_seq += 1
        ge = GameInputEvent(event_id=f"live_ctrl_input_{self._event_seq}", session_id=self.live_debug_session_id, game_id=self.game_id, input_type="pointer_click", created_at_ms=int(time.time() * 1000), source="minimal_game_canvas", x_norm=float(payload.get("x_norm", 0.0)), y_norm=float(payload.get("y_norm", 0.0)), button=0, raw_event_type="pointer_click", debug_hit=payload.get("hit"), payload=dict(payload))
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
        return {"result": result, "status": "accepted", "reason": result, "source": "live_control", "game_input": ge.to_dict(), "last_game_event": dict(self.last_game_event), "game_event_count": self.game_event_count, "platform_message_count": self._platform_adapter.platform_message_count, "last_platform_message": dict(self._platform_adapter.last_platform_message), "last_platform_result": self._platform_adapter.last_platform_result}

    def get_runtime_snapshot(self) -> dict[str, Any]:
        rt = self._live_source.get_runtime_snapshot()
        with self._lock:
            rt.update({"source": "live_control", "game_update_count": self.game_update_count, "last_runtime_attention": self.last_runtime_attention, "last_runtime_attention_fresh": self.last_runtime_attention_fresh, "last_runtime_gyro_fresh": self.last_runtime_gyro_fresh, "interaction_enabled": self.interaction_enabled, "live_debug_session_id": self.live_debug_session_id or "", "game_event_count": self.game_event_count})
        return rt

    def get_app_state(self) -> dict[str, Any]:
        base = self._live_source.get_app_state()
        base.update({"source": "live_control", "current_user_id": self.user_id, "current_game_id": self.game_id, "session_active": self.interaction_enabled, "allowed_commands": ["refresh_snapshot", "load_demo_user", "start_mock_session", "end_session", "open_last_report"]})
        return base

    def get_session_state(self) -> dict[str, Any]:
        return {"session_id": self.live_debug_session_id or "", "user_id": self.user_id, "game_id": self.game_id, "session_active": self.interaction_enabled, "score": self.last_game_view.get("score", 0), "warning_count": 0, "error_count": 0, "log_path": "", "report_path": "", "platform_report_status": "mock_only", "source": "live_control"}

    def get_game_view(self) -> dict[str, Any]:
        return dict(self.last_game_view)
