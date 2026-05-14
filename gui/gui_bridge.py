from __future__ import annotations

from json import JSONDecodeError, dumps, loads

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
        self._app_state = "{}"
        self._runtime_snapshot = "{}"
        self._session_state = "{}"
        self._game_view_json = "{}"
        self._last_command = ""
        self._last_event = ""
        self._command_count = 0
        self._event_count = 0
        self._last_command_result = ""
        self._last_event_result = ""
        self._last_pointer_x = ""
        self._last_pointer_y = ""
        self._last_hit_state = ""
        self._game_event_count = 0
        self._last_game_event = ""
        self._last_game_event_type = ""
        self._last_game_action_name = ""
        self._last_game_target_index = ""
        self._game_view_score = ""
        self._game_view_combo = ""
        self._game_view_entity_count = ""
        self._game_view_visual_event_count = ""
        self._platform_message_count = 0
        self._last_platform_message = ""
        self._last_platform_index = ""
        self._last_platform_action = ""
        self._last_platform_result = ""
        self._refresh_internal()

    def _refresh_internal(self) -> None:
        self._app_state = dumps(self._facade.get_app_state())
        self._runtime_snapshot = dumps(self._facade.get_runtime_snapshot())
        self._session_state = dumps(self._facade.get_session_state())
        self._game_view_json = dumps(self._facade.get_game_view())
        self._command_count = self._facade.command_count
        self._event_count = self._facade.event_count
        self._last_command = dumps(self._facade.last_command) if self._facade.last_command else ""
        self._last_event = dumps(self._facade.last_event) if self._facade.last_event else ""
        self._last_command_result = dumps(self._facade.last_command_result) if self._facade.last_command_result else ""
        self._last_event_result = dumps(self._facade.last_event_result) if self._facade.last_event_result else ""
        self._last_pointer_x = "" if self._facade.last_pointer_x is None else str(self._facade.last_pointer_x)
        self._last_pointer_y = "" if self._facade.last_pointer_y is None else str(self._facade.last_pointer_y)
        self._last_hit_state = "" if self._facade.last_hit_state is None else ("true" if self._facade.last_hit_state else "false")
        self._game_event_count = self._facade.game_event_count
        self._last_game_event = dumps(self._facade.last_game_event) if self._facade.last_game_event else ""
        self._last_game_event_type = self._facade.last_game_event_type
        self._last_game_action_name = self._facade.last_game_action_name
        self._last_game_target_index = "" if self._facade.last_game_target_index is None else str(self._facade.last_game_target_index)
        summary = self._facade.last_game_view_summary
        self._game_view_score = str(summary.get("score", "")) if summary else ""
        self._game_view_combo = str(summary.get("combo", "")) if summary else ""
        self._game_view_entity_count = str(summary.get("entity_count", "")) if summary else ""
        self._game_view_visual_event_count = str(summary.get("visual_event_count", "")) if summary else ""
        self._platform_message_count = self._facade.platform_message_count
        self._last_platform_message = dumps(self._facade.last_platform_message) if self._facade.last_platform_message else ""
        self._last_platform_index = "" if self._facade.last_platform_index is None else str(self._facade.last_platform_index)
        self._last_platform_action = self._facade.last_platform_action
        self._last_platform_result = self._facade.last_platform_result
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

    @Property(str, notify=stateChanged)
    def gameViewJson(self) -> str:
        return self._game_view_json

    @Property(int, notify=stateChanged)
    def commandCount(self) -> int:
        return self._command_count

    @Property(str, notify=stateChanged)
    def lastCommand(self) -> str:
        return self._last_command


    @Property(str, notify=stateChanged)
    def lastCommandResult(self) -> str:
        return self._last_command_result

    @Property(int, notify=stateChanged)
    def eventCount(self) -> int:
        return self._event_count

    @Property(str, notify=stateChanged)
    def lastEvent(self) -> str:
        return self._last_event


    @Property(str, notify=stateChanged)
    def lastEventResult(self) -> str:
        return self._last_event_result

    @Property(str, notify=stateChanged)
    def lastPointerX(self) -> str:
        return self._last_pointer_x

    @Property(str, notify=stateChanged)
    def lastPointerY(self) -> str:
        return self._last_pointer_y

    @Property(str, notify=stateChanged)
    def lastHitState(self) -> str:
        return self._last_hit_state

    @Property(int, notify=stateChanged)
    def gameEventCount(self) -> int:
        return self._game_event_count

    @Property(str, notify=stateChanged)
    def lastGameEvent(self) -> str:
        return self._last_game_event

    @Property(str, notify=stateChanged)
    def lastGameEventType(self) -> str:
        return self._last_game_event_type

    @Property(str, notify=stateChanged)
    def lastGameActionName(self) -> str:
        return self._last_game_action_name

    @Property(str, notify=stateChanged)
    def lastGameTargetIndex(self) -> str:
        return self._last_game_target_index

    @Property(str, notify=stateChanged)
    def gameViewScore(self) -> str:
        return self._game_view_score

    @Property(str, notify=stateChanged)
    def gameViewCombo(self) -> str:
        return self._game_view_combo

    @Property(str, notify=stateChanged)
    def gameViewEntityCount(self) -> str:
        return self._game_view_entity_count

    @Property(str, notify=stateChanged)
    def gameViewVisualEventCount(self) -> str:
        return self._game_view_visual_event_count

    @Property(int, notify=stateChanged)
    def platformMessageCount(self) -> int:
        return self._platform_message_count

    @Property(str, notify=stateChanged)
    def lastPlatformMessage(self) -> str:
        return self._last_platform_message

    @Property(str, notify=stateChanged)
    def lastPlatformIndex(self) -> str:
        return self._last_platform_index

    @Property(str, notify=stateChanged)
    def lastPlatformAction(self) -> str:
        return self._last_platform_action

    @Property(str, notify=stateChanged)
    def lastPlatformResult(self) -> str:
        return self._last_platform_result

    @Slot()
    def refresh(self) -> None:
        self._facade.handle_gui_command("refresh_snapshot", {})
        self._refresh_internal()

    @Slot(str, str)
    def sendCommand(self, command: str, args_json: str = "{}") -> None:
        try:
            args = loads(args_json or "{}")
        except JSONDecodeError:
            print(f"[GUI BRIDGE ERROR] invalid args_json for command={command}: {args_json}", flush=True)
            args = {}
        self._facade.handle_gui_command(command, args)
        self._refresh_internal()

    @Slot(str, str)
    def sendEvent(self, event_type: str, payload_json: str = "{}") -> None:
        try:
            payload = loads(payload_json or "{}")
        except JSONDecodeError:
            print(
                f"[GUI BRIDGE ERROR] invalid payload_json for event_type={event_type}: {payload_json}",
                flush=True,
            )
            payload = {}
        self._facade.handle_gui_event(event_type, payload)
        self._refresh_internal()
