from __future__ import annotations

from pathlib import Path


def test_qt_app_has_split_refresh_pumps() -> None:
    code = Path("gui/qt_app.py").read_text(encoding="utf-8")
    assert "QTimer" in code
    assert "GUI_REFRESH_INTERVAL_MS = 100" in code
    assert "GAME_REFRESH_INTERVAL_MS = 50" in code
    assert "setInterval(GUI_REFRESH_INTERVAL_MS)" in code
    assert "setInterval(GAME_REFRESH_INTERVAL_MS)" in code
    assert "timeout.connect(bridge.update_state_from_facade)" in code
    assert "timeout.connect(bridge.update_game_state_from_facade)" in code


def test_bridge_separates_full_refresh_from_game_view_refresh() -> None:
    code = Path("gui/gui_bridge.py").read_text(encoding="utf-8")
    for token in [
        "appStateChanged = Signal()",
        "runtimeSnapshotChanged = Signal()",
        "sessionStateChanged = Signal()",
        "gameHudJsonChanged = Signal()",
        "gameViewJsonChanged = Signal()",
        "def update_state_from_facade(self)",
        "def update_game_state_from_facade(self)",
        "Do not fetch or emit gameView/gameHud here",
        "self.gameHudJsonChanged.emit()",
        "self.gameViewJsonChanged.emit()",
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
        "onGameViewJsonChanged",
        "pullGameState",
    ]:
        assert token in qml

    for banned in ["ScrollView", "GameCanvas {", "Repeater"]:
        assert banned not in qml
