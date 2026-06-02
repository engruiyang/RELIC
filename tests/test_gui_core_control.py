import pytest

from gui.gui_facade import GuiFacade

PySide6 = pytest.importorskip("PySide6")

from gui.gui_bridge import GuiBridge


def test_core_control_facade_and_bridge(tmp_path) -> None:
    facade = GuiFacade(mode="core-control", db_path=str(tmp_path / "relic.db"), duration_sec=1)
    assert facade.get_app_state()["source"] == "core_control"
    facade.handle_gui_event("target_click", {"x_norm": 0.5, "y_norm": 0.5, "button": "left"})
    assert facade.event_count >= 1
    assert facade.last_event_result
    assert facade.last_event_result["result"] == "game_event_recorded_no_session_context"
    assert facade.platform_message_count == 0
    bridge = GuiBridge(facade)
    bridge.sendCommand("refresh_snapshot", "{}")
    assert bridge.commandCount >= 1
    assert "accepted" in bridge.lastCommandResult
