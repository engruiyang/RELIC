from __future__ import annotations

import time

from gui.gui_facade import GuiFacade


class FakeLiveReadonlySource:
    def __init__(self, host: str, port: int, poll_interval_sec: float = 0.01):
        self.host = host
        self.port = port
        self.poll_interval_sec = poll_interval_sec
        self.connection_status = "connected"
        self._count = 0
        self.stopped = False

    def start(self):
        return None

    def stop(self):
        self.stopped = True

    def get_runtime_snapshot(self):
        self._count += 1
        return {
            "attention": 70,
            "attention_age_ms": 20,
            "attention_fresh": True,
            "gyro_x": 1.0,
            "gyro_y": 2.0,
            "gyro_z": 3.0,
            "gyro_age_ms": 20,
            "gyro_fresh": True,
            "stream_alive": True,
            "connection_status": self.connection_status,
            "raw_message_count": self._count,
            "decoded_attention_count": self._count,
            "decoded_gyro_count": self._count,
            "current_warning_flags": [],
            "historical_warning_flags": [],
            "error_flags": [],
            "error_message": None,
            "source": "live_readonly",
            "fi": 0.0,
            "sqi": 0.0,
        }

    def get_app_state(self):
        return {"state": "READY", "source": "live_readonly", "allowed_commands": []}

    def get_session_state(self):
        return {"session_id": "", "session_active": False, "source": "live_readonly"}


def test_live_control_flow(monkeypatch):
    monkeypatch.setattr("gui.gui_live_control_source.GuiLiveReadonlySource", FakeLiveReadonlySource)
    facade = GuiFacade(mode="live-control", host="127.0.0.1", port=8000)
    assert facade.get_app_state()["source"] == "live_control"
    time.sleep(0.05)
    rt = facade.get_runtime_snapshot()
    assert rt["attention"] == 70
    assert rt["game_update_count"] > 0

    facade.handle_gui_event("pointer_click", {"x_norm": 0.5, "y_norm": 0.5})
    assert facade.last_event_result["result"] == "no_active_live_debug_session"

    facade.handle_gui_command("start_mock_session", {})
    assert facade.last_command_result["status"] == "live_debug_started"
    sid1 = facade.last_command_result["session_id"]

    facade.handle_gui_event("pointer_click", {"x_norm": 0.5, "y_norm": 0.5})
    assert facade.last_event_result["result"] == "game_event_recorded_and_platform_mocked"
    gi = facade.last_event_result["game_input"]
    ge = facade.last_event_result["last_game_event"]
    pm = facade.last_event_result["last_platform_message"]
    assert gi["session_id"] == ge["session_id"] == pm["session_id"] == sid1

    time.sleep(1.1)
    facade.handle_gui_command("start_mock_session", {})
    sid2 = facade.last_command_result["session_id"]
    assert sid2 != sid1

    facade.handle_gui_command("end_session", {})
    assert facade.last_command_result["status"] in {"live_debug_stopped", "noop"}
    facade.handle_gui_event("pointer_click", {"x_norm": 0.1, "y_norm": 0.1})
    assert facade.last_event_result["result"] == "no_active_live_debug_session"

    facade.handle_gui_command("open_last_report", {})
    assert facade.last_command_result["status"] == "noop"
    facade.close()


def test_live_control_connect_fail_visible(monkeypatch):
    class FailFake(FakeLiveReadonlySource):
        def __init__(self, host: str, port: int, poll_interval_sec: float = 0.01):
            super().__init__(host, port, poll_interval_sec)
            self.connection_status = "connect_failed"

    monkeypatch.setattr("gui.gui_live_control_source.GuiLiveReadonlySource", FailFake)
    facade = GuiFacade(mode="live-control")
    assert facade.get_runtime_snapshot()["connection_status"] == "connect_failed"
    facade.close()
