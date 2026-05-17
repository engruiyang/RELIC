from __future__ import annotations

from pathlib import Path


def test_qt_app_has_low_frequency_refresh_pump() -> None:
    code = Path("gui/qt_app.py").read_text(encoding="utf-8")
    assert "QTimer" in code
    assert "GUI_REFRESH_INTERVAL_MS = 500" in code
    assert "setInterval(GUI_REFRESH_INTERVAL_MS)" in code
    assert "interval: 100" not in code
    assert "timeout.connect(bridge.update_state_from_facade)" in code


def test_bridge_has_notify_signals_and_update_method() -> None:
    code = Path("gui/gui_bridge.py").read_text(encoding="utf-8")
    for token in [
        "appStateChanged = Signal()",
        "runtimeSnapshotChanged = Signal()",
        "sessionStateChanged = Signal()",
        "gameHudJsonChanged = Signal()",
        "def update_state_from_facade(self)",
        "self.appStateChanged.emit()",
        "self.runtimeSnapshotChanged.emit()",
        "self.sessionStateChanged.emit()",
        "self.gameHudJsonChanged.emit()",
    ]:
        assert token in code


def test_qml_binding_and_no_banned_structures() -> None:
    qml = Path("ui_qml/MinimalGui.qml").read_text(encoding="utf-8")
    for token in [
        "guiBridge.appState",
        "guiBridge.runtimeSnapshot",
        "guiBridge.sessionState",
        "guiBridge.gameHudJson",
        "Connections",
        "onStateChanged",
    ]:
        assert token in qml

    for banned in ["interval: 100", "ScrollView", "GameCanvas {", "Loader", "Repeater"]:
        assert banned not in qml
