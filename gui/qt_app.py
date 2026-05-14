from __future__ import annotations

from pathlib import Path

from .gui_bridge import GuiBridge
from .gui_facade import GuiFacade


def run_minimal_qt(mode: str = "mock", db_path: str = "data/relic_local.db") -> int:
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine

    app = QGuiApplication([])
    facade = GuiFacade(mode=mode, db_path=db_path)
    bridge = GuiBridge(facade)

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("guiBridge", bridge)
    qml_path = Path(__file__).resolve().parent.parent / "ui_qml" / "MinimalGui.qml"
    engine.load(str(qml_path))
    if not engine.rootObjects():
        return 1
    return app.exec()
