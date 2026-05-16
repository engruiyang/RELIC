from gui.gui_facade import GuiFacade


def test_mock_gui_facade_app_state() -> None:
    facade = GuiFacade(mode="mock")
    assert facade.get_app_state()["state"] == "READY"
    assert facade.get_app_state()["source"] == "mock"


def test_mock_gui_facade_runtime_snapshot() -> None:
    facade = GuiFacade(mode="mock")
    assert facade.get_runtime_snapshot()["control_state"] == "STABLE_FOCUS"


def test_mock_gui_facade_session_state() -> None:
    facade = GuiFacade(mode="mock")
    assert "session_id" in facade.get_session_state()


def test_gui_facade_records_command() -> None:
    facade = GuiFacade(mode="mock")
    facade.handle_gui_command("start_mock_session", {})
    assert facade.command_count == 1
    assert "start_mock_session" in str(facade.last_command)
    assert facade.received_commands[-1]["command"] == "start_mock_session"


def test_gui_facade_records_event() -> None:
    facade = GuiFacade(mode="mock")
    payload = {"target_id": "mock_target_0"}
    facade.handle_gui_event("target_click", payload)
    assert facade.event_count == 1
    assert "target_click" in str(facade.last_event)
    assert facade.received_events[-1]["event_type"] == "target_click"


def test_core_gui_facade_readonly_command_handling(tmp_path) -> None:
    facade = GuiFacade(mode="core", db_path=str(tmp_path / "relic.db"))
    assert facade.get_app_state()["source"] == "core_readonly"
    assert "source" in facade.get_runtime_snapshot()
    assert facade.get_session_state()["source"] == "core_readonly"
    facade.handle_gui_command("refresh_snapshot", {})
    assert facade.last_command_result["status"] == "accepted"
    facade.handle_gui_command("start_mock_session", {})
    assert facade.last_command_result["reason"] == "readonly_rejected"
    facade.handle_gui_event("target_click", {"x_norm": 0.5})
    assert facade.last_event_result["reason"] == "readonly_ignored"
