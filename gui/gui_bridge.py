from __future__ import annotations

from json import dumps, loads

from .gui_facade import GuiFacade

try:
    from PySide6.QtCore import QObject, Property, Signal, Slot
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PySide6 is required for GUI bridge") from exc


class GuiBridge(QObject):
    stateChanged = Signal()

    def __init__(self, facade: GuiFacade) -> None:
        super().__init__()
        self._facade = facade
        self._app_state = dumps(self._facade.get_app_state())
        self._runtime_snapshot = dumps(self._facade.get_runtime_snapshot())
        self._session_state = dumps(self._facade.get_session_state())

    def _refresh_internal(self) -> None:
        self._app_state = dumps(self._facade.get_app_state())
        self._runtime_snapshot = dumps(self._facade.get_runtime_snapshot())
        self._session_state = dumps(self._facade.get_session_state())
        self.stateChanged.emit()

    @Property(str, notify=stateChanged)
    def appState(self) -> str:
        return self._app_state

    @Property(str, notify=stateChanged)
    def runtimeSnapshot(self) -> str:
        return self._runtime_snapshot

    @Property(str, notify=stateChanged)
    def sessionState(self) -> str:
        return self._session_state

    @Slot()
    def refresh(self) -> None:
        self._facade.handle_gui_command("refresh_snapshot", {})
        self._refresh_internal()

    @Slot(str, str)
    def sendCommand(self, command: str, args_json: str = "{}") -> None:
        self._facade.handle_gui_command(command, loads(args_json or "{}"))
        self._refresh_internal()

    @Slot(str, str)
    def sendEvent(self, event_type: str, payload_json: str = "{}") -> None:
        self._facade.handle_gui_event(event_type, loads(payload_json or "{}"))
