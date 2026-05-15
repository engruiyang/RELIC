from __future__ import annotations

import time

from game.game_client_registry import create_game_client
from gui.gui_facade import GuiFacade


class FakeLiveReadonlySource:
    def __init__(self, host: str, port: int, poll_interval_sec: float = 0.01):
        self.host = host
        self.port = port
        self.poll_interval_sec = poll_interval_sec
        self._count = 0

    def start(self):
        return None

    def stop(self):
        return None

    def get_runtime_snapshot(self):
        self._count += 1
        return {
            "attention": 70,
            "attention_age_ms": 20,
            "attention_fresh": True,
            "gyro_fresh": True,
            "stream_alive": True,
            "control_state": "HIGH_FOCUS",
            "warning_flags": [],
            "error_flags": [],
            "source": "live_readonly",
        }

    def get_app_state(self):
        return {"state": "READY", "source": "live_readonly", "allowed_commands": []}

    def get_session_state(self):
        return {"session_id": "", "session_active": False, "source": "live_readonly"}


def test_registry_supports_fake_and_trace_lock() -> None:
    assert create_game_client("fake_game").game_id == "fake_game"
    assert create_game_client("trace_lock").game_id == "trace_lock"


def test_live_control_trace_lock_flow(monkeypatch) -> None:
    monkeypatch.setattr("gui.gui_live_control_source.GuiLiveReadonlySource", FakeLiveReadonlySource)
    facade = GuiFacade(mode="live-control", game_id="trace_lock", host="127.0.0.1", port=8000)

    bundle = facade.get_render_resources()
    assert bundle["game_id"] == "trace_lock"
    assert "tracelock.target.marked_trace" in bundle["assets"]

    app_state = facade.get_app_state()
    assert app_state["current_game_id"] == "trace_lock"

    facade.handle_gui_command("start_mock_session", {})
    assert facade.last_command_result["status"] == "live_debug_started"
    sid = facade.last_command_result["session_id"]

    target = None
    for _ in range(50):
        view = facade.get_game_view()
        targets = [e for e in view.get("entities", []) if e.get("kind") == "target"]
        if targets:
            target = targets[0]
            break
        time.sleep(0.01)
    assert target is not None
    facade.handle_gui_event("pointer_click", {"x_norm": target["x"], "y_norm": target["y"]})
    assert facade.last_game_event_type == "target_click"
    assert facade.last_game_event.get("reportable") is True
    assert facade.last_platform_index == 0
    assert facade.last_event_result["game_input"]["session_id"] == sid
    assert facade.last_game_event["session_id"] == sid
    assert facade.last_platform_message.get("session_id") == sid

    facade.handle_gui_event("pointer_click", {"x_norm": 0.0, "y_norm": 0.0})
    assert facade.last_game_event_type == "background_click"
    assert facade.last_platform_index == 1

    before = facade.platform_message_count
    facade._live_control_source._client.update({}, 2000)  # force timeout from level-1 lifetime
    omitted = [e for e in facade._live_control_source._client.collect_game_events() if e.event_type == "target_omitted"]
    assert omitted and omitted[0].reportable is False
    assert facade.platform_message_count == before

    facade.handle_gui_command("end_session", {})
    assert facade.last_command_result["status"] in {"live_debug_stopped", "noop"}
    facade.handle_gui_event("pointer_click", {"x_norm": 0.3, "y_norm": 0.3})
    assert facade.last_event_result["result"] == "no_active_live_debug_session"

    facade.close()


def test_live_control_fake_game_still_works(monkeypatch) -> None:
    monkeypatch.setattr("gui.gui_live_control_source.GuiLiveReadonlySource", FakeLiveReadonlySource)
    facade = GuiFacade(mode="live-control", game_id="fake_game", host="127.0.0.1", port=8000)
    facade.handle_gui_command("start_mock_session", {})
    facade.handle_gui_event("pointer_click", {"x_norm": 0.5, "y_norm": 0.5})
    assert facade.last_event_result["result"] == "game_event_recorded_and_platform_mocked"
    facade.close()
