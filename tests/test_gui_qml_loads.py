from __future__ import annotations

import os
from pathlib import Path

import pytest

PySide6 = pytest.importorskip("PySide6")
from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


class _Bridge(QObject):
    stateChanged = Signal()
    appStateChanged = Signal()
    runtimeSnapshotChanged = Signal()
    sessionStateChanged = Signal()
    gameHudJsonChanged = Signal()
    controlManifestJsonChanged = Signal()
    controlStateJsonChanged = Signal()

    @Property(str, notify=appStateChanged)
    def appState(self): return "{}"

    @Property(str, notify=runtimeSnapshotChanged)
    def runtimeSnapshot(self): return "{}"

    @Property(str, notify=sessionStateChanged)
    def sessionState(self): return "{}"

    @Property(str, notify=gameHudJsonChanged)
    def gameHudJson(self): return "{}"

    @Property(str, notify=controlManifestJsonChanged)
    def controlManifestJson(self): return "[]"

    @Property(str, notify=controlStateJsonChanged)
    def controlStateJson(self): return "{}"

    @Slot(str, str, result=str)
    def invokeAction(self, action_id: str, payload_json: str = "{}") -> str:
        return '{"status":"ok","action_id":"%s"}' % action_id


def test_qml_loads_with_engine() -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QGuiApplication.instance() or QGuiApplication([])
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("guiBridge", _Bridge())
    qml_path = Path("ui_qml/MinimalGui.qml").resolve()
    engine.load(str(qml_path))
    assert engine.rootObjects(), f"QML failed to load: {qml_path}"
    if app is not None:
        app.quit()
