from gui.gui_facade import GuiFacade


class FakeLiveSource:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.started = False
        self.stopped = False
        self.runtime = {
            "attention": 66,
            "attention_age_ms": 80,
            "attention_fresh": True,
            "gyro_x": 1.1,
            "gyro_y": 2.2,
            "gyro_z": 3.3,
            "gyro_age_ms": 50,
            "gyro_fresh": True,
            "stream_alive": True,
            "connection_status": "connected",
            "raw_message_count": 10,
            "decoded_attention_count": 3,
            "decoded_gyro_count": 7,
            "current_warning_flags": [],
            "historical_warning_flags": ["attention_missing"],
            "error_flags": [],
            "error_message": None,
            "source": "live_readonly",
            "fi": 0.0,
            "sqi": 0.0,
            "control_state": "UNRELIABLE_SIGNAL",
            "warning_flags": [],
        }

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True

    def get_runtime_snapshot(self):
        return dict(self.runtime)

    def get_app_state(self):
        return {
            "state": "READY",
            "source": "live_readonly",
            "allowed_commands": ["refresh_snapshot", "load_demo_user", "end_session"],
            "current_user_id": "",
            "current_user_name": "",
            "device_connected": True,
            "calibration_status": "unknown",
            "session_active": False,
            "current_game_id": "",
            "warning_flags": [],
            "error_flags": [],
        }

    def get_session_state(self):
        return {"session_id": "", "source": "live_readonly", "session_active": False}


def test_live_readonly_facade_basics(monkeypatch):
    monkeypatch.setattr("gui.gui_facade.GuiLiveReadonlySource", FakeLiveSource)
    facade = GuiFacade(mode="live-readonly")
    assert facade.get_app_state()["source"] == "live_readonly"
    rt = facade.get_runtime_snapshot()
    assert rt["attention"] == 66
    assert rt["gyro_x"] == 1.1
    assert rt["raw_message_count"] == 10
    assert rt["decoded_attention_count"] == 3
    assert rt["decoded_gyro_count"] == 7

    facade.handle_gui_command("refresh_snapshot", {})
    assert facade.last_command_result["status"] == "accepted"
    facade.handle_gui_command("start_mock_session", {})
    assert facade.last_command_result["status"] == "readonly_rejected"
    facade.handle_gui_command("end_session", {})
    assert facade.last_command_result["status"] == "noop"

    facade.handle_gui_event("pointer_click", {"x_norm": 0.5, "y_norm": 0.5})
    assert facade.last_event_result["result"] == "readonly_ignored"
    assert facade.game_event_count == 0
    assert facade.platform_message_count == 0
    facade.close()
    assert facade._live_source.stopped is True


def test_live_readonly_connect_fail_visible(monkeypatch):
    class FailLiveSource(FakeLiveSource):
        def start(self):
            self.started = True
            self.runtime["connection_status"] = "connect_failed"
            self.runtime["error_flags"] = ["connect_failed"]
            self.runtime["error_message"] = "boom"

    monkeypatch.setattr("gui.gui_facade.GuiLiveReadonlySource", FailLiveSource)
    facade = GuiFacade(mode="live-readonly")
    rt = facade.get_runtime_snapshot()
    assert rt["connection_status"] == "connect_failed"
    assert "connect_failed" in rt["error_flags"]


def test_existing_modes_unchanged():
    assert GuiFacade(mode="mock").get_app_state()["source"] == "mock"
    assert GuiFacade(mode="core", db_path=":memory:").get_app_state()["source"] == "core_readonly"
