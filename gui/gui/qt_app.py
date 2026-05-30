from __future__ import annotations

from pathlib import Path

from .gui_bridge import GuiBridge
from .gui_facade import GuiFacade

GUI_REFRESH_INTERVAL_MS = 500


def run_minimal_qt(mode: str = "mock", db_path: str = "data/relic_local.db", duration_sec: int = 3, user_id: str = "demo_user", game_id: str = "fake_game", task6b_config: str = "config/task6b.yaml", host: str = "127.0.0.1", port: int = 8000) -> int:
    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine

    app = QGuiApplication([])
    facade = GuiFacade(mode=mode, db_path=db_path, duration_sec=duration_sec, user_id=user_id, game_id=game_id, task6b_config=task6b_config, host=host, port=port)
    bridge = GuiBridge(facade)

    refresh_timer = QTimer()
    refresh_timer.setInterval(GUI_REFRESH_INTERVAL_MS)
    refresh_timer.timeout.connect(bridge.update_state_from_facade)
    refresh_timer.start()

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("guiBridge", bridge)
    qml_path = Path(__file__).resolve().parent.parent / "ui_qml" / "MinimalGui.qml"
    engine.load(str(qml_path))
    if not engine.rootObjects():
        print(f"[GUI ERROR] QML load failed path={qml_path}", flush=True)
        print("[GUI ERROR] rootObjects empty; check QML syntax", flush=True)
        return 1
    try:
        return app.exec()
    finally:
        facade.close()
