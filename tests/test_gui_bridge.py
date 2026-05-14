import pytest

from gui.gui_facade import GuiFacade

PySide6 = pytest.importorskip("PySide6")

from gui.gui_bridge import GuiBridge


def test_gui_bridge_can_create() -> None:
    facade = GuiFacade(mode="mock")
    bridge = GuiBridge(facade)
    assert "demo_user" in bridge.appState
