from __future__ import annotations

import os
from pathlib import Path

from .gui_bridge import GuiBridge
from .gui_facade import GuiFacade

GUI_REFRESH_INTERVAL_MS = 100
GAME_REFRESH_INTERVAL_MS = 50


def run_minimal_qt(mode: str = "mock", db_path: str = "data/relic_local.db", duration_sec: int = 3, user_id: str = "demo_user", game_id: str = "fake_game", task6b_config: str = "config/task6b.yaml", host: str = "127.0.0.1", port: int = 8000) -> int:
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")

    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine
    try:
        from PySide6.QtQuickControls2 import QQuickStyle
        QQuickStyle.setStyle(os.environ.get("QT_QUICK_CONTROLS_STYLE", "Basic"))
    except Exception:
        # Older/minimal PySide6 installations may omit QtQuickControls2 in tests.
        # The environment variable above still covers normal GUI runs.
        pass

    app = QGuiApplication([])
    facade = GuiFacade(mode=mode, db_path=db_path, duration_sec=duration_sec, user_id=user_id, game_id=game_id, task6b_config=task6b_config, host=host, port=port)
    bridge = GuiBridge(facade)

    # Keep the full GUI refresh in the realtime-friendly range. It still
    # carries session/runtime/control objects, while the separate game timer
    # below keeps GameCanvas at the lower-latency cadence.
    refresh_timer = QTimer()
    refresh_timer.setInterval(GUI_REFRESH_INTERVAL_MS)
    refresh_timer.timeout.connect(bridge.update_state_from_facade)
    refresh_timer.start()

    # Restore the original responsive GameCanvas feedback cadence without
    # creating another game pipeline: this timer only pulls the existing
    # facade game view/HUD and emits the existing gameView/gameHud signals.
    game_refresh_timer = QTimer()
    game_refresh_timer.setInterval(GAME_REFRESH_INTERVAL_MS)
    game_refresh_timer.timeout.connect(bridge.update_game_state_from_facade)
    game_refresh_timer.start()

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
