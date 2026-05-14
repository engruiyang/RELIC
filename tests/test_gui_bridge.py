import json

import pytest

from gui.gui_facade import GuiFacade

PySide6 = pytest.importorskip("PySide6")

from gui.gui_bridge import GuiBridge


def test_gui_bridge_can_create() -> None:
    facade = GuiFacade(mode="mock")
    bridge = GuiBridge(facade)
    assert "demo_user" in bridge.appState


def test_gui_bridge_send_command() -> None:
    facade = GuiFacade(mode="mock")
    bridge = GuiBridge(facade)
    bridge.sendCommand("start_mock_session", "{}")
    assert facade.received_commands[-1]["command"] == "start_mock_session"
    assert bridge.commandCount == 1


def test_gui_bridge_send_event() -> None:
    facade = GuiFacade(mode="mock")
    bridge = GuiBridge(facade)
    bridge.sendEvent("target_click", json.dumps({"target_id": "mock_target_0"}))
    assert facade.received_events[-1]["event_type"] == "target_click"
    assert bridge.eventCount == 1
