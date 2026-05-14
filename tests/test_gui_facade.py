from gui.gui_facade import GuiFacade


def test_mock_gui_facade_app_state() -> None:
    facade = GuiFacade(mode="mock")
    assert facade.get_app_state()["state"] == "READY"


def test_mock_gui_facade_runtime_snapshot() -> None:
    facade = GuiFacade(mode="mock")
    assert facade.get_runtime_snapshot()["control_state"] == "STABLE_FOCUS"


def test_mock_gui_facade_session_state() -> None:
    facade = GuiFacade(mode="mock")
    assert facade.get_session_state()["session_id"] == "mock_session"


def test_gui_command_recorded() -> None:
    facade = GuiFacade(mode="mock")
    facade.handle_gui_command("start_mock_session", {})
    assert facade.received_commands[-1]["command"] == "start_mock_session"


def test_gui_event_recorded() -> None:
    facade = GuiFacade(mode="mock")
    payload = {"target_id": "mock_target_0"}
    facade.handle_gui_event("target_click", payload)
    assert facade.received_events[-1]["event_type"] == "target_click"
