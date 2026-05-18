from __future__ import annotations

from json import JSONDecodeError, dumps, loads

from .gui_facade import GuiFacade

try:
    from PySide6.QtCore import QObject, Property, Signal, Slot
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PySide6 is required for GUI bridge") from exc


class GuiBridge(QObject):
    stateChanged = Signal()
    appStateChanged = Signal()
    runtimeSnapshotChanged = Signal()
    sessionStateChanged = Signal()
    gameHudJsonChanged = Signal()
    controlManifestJsonChanged = Signal()
    controlStateJsonChanged = Signal()
    pageCommandManifestJsonChanged = Signal()

    def __init__(self, facade: GuiFacade) -> None:
        super().__init__()
        self._facade = facade
        self._app_state = "{}"
        self._runtime_snapshot = "{}"
        self._session_state = "{}"
        self._game_view_json = "{}"
        self._render_resources_json = "{}"
        self._game_hud_json = "{}"
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
        self._control_manifest_json = "[]"
        self._control_state_json = "{}"
        self._page_command_manifest_json = "{}"
        self.update_state_from_facade()

    def update_state_from_facade(self) -> None:
        next_app_state = dumps(self._facade.get_app_state())
        next_runtime_snapshot = dumps(self._facade.get_runtime_snapshot())
        next_session_state = dumps(self._facade.get_session_state())
        next_game_hud_json = dumps(self._facade.get_game_hud(), ensure_ascii=False)
        next_control_manifest_json = dumps(self._facade.get_control_manifest(), ensure_ascii=False)
        next_control_state_json = dumps(self._facade.get_control_state(), ensure_ascii=False)
        next_page_command_manifest_json = dumps(self._facade.get_page_command_manifest(), ensure_ascii=False)

        changed = False
        if next_app_state != self._app_state:
            self._app_state = next_app_state
            self.appStateChanged.emit()
            changed = True
        if next_runtime_snapshot != self._runtime_snapshot:
            self._runtime_snapshot = next_runtime_snapshot
            self.runtimeSnapshotChanged.emit()
            changed = True
        if next_session_state != self._session_state:
            self._session_state = next_session_state
            self.sessionStateChanged.emit()
            changed = True
        if next_game_hud_json != self._game_hud_json:
            self._game_hud_json = next_game_hud_json
            self.gameHudJsonChanged.emit()
            changed = True
        if next_control_manifest_json != self._control_manifest_json:
            self._control_manifest_json = next_control_manifest_json
            self.controlManifestJsonChanged.emit()
            changed = True
        if next_control_state_json != self._control_state_json:
            self._control_state_json = next_control_state_json
            self.controlStateJsonChanged.emit()
            changed = True
        if next_page_command_manifest_json != self._page_command_manifest_json:
            self._page_command_manifest_json = next_page_command_manifest_json
            self.pageCommandManifestJsonChanged.emit()
            changed = True

        self._game_view_json = dumps(self._facade.get_game_view())
        self._render_resources_json = dumps(self._facade.get_render_resources(), ensure_ascii=False)
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

        if changed:
            self.stateChanged.emit()

    @Property(str, notify=appStateChanged)
    def appState(self) -> str:
        return self._app_state

    @Property(str, notify=runtimeSnapshotChanged)
    def runtimeSnapshot(self) -> str:
        return self._runtime_snapshot

    @Property(str, notify=sessionStateChanged)
    def sessionState(self) -> str:
        return self._session_state

    @Property(str, notify=stateChanged)
    def gameViewJson(self) -> str:
        return self._game_view_json

    @Property(str, notify=stateChanged)
    def renderResourcesJson(self) -> str:
        return self._render_resources_json

    @Property(str, notify=gameHudJsonChanged)
    def gameHudJson(self) -> str:
        return self._game_hud_json

    @Property(str, notify=controlManifestJsonChanged)
    def controlManifestJson(self) -> str:
        return self._control_manifest_json

    @Property(str, notify=controlStateJsonChanged)
    def controlStateJson(self) -> str:
        return self._control_state_json

    @Property(str, notify=pageCommandManifestJsonChanged)
    def pageCommandManifestJson(self) -> str:
        return self._page_command_manifest_json

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
        self._facade.handle_gui_command("refresh_snapshot", {"silent": True})
        self.update_state_from_facade()

    @Slot(str, str, result=str)
    def invokeAction(self, action_id: str, payload_json: str = "{}") -> str:
        try:
            payload = loads(payload_json or "{}")
        except JSONDecodeError:
            payload = {}
        result = self._facade.invoke_action(action_id, payload)
        self.update_state_from_facade()
        return dumps(result, ensure_ascii=False)

    @Slot(str, str)
    def sendCommand(self, command: str, args_json: str = "{}") -> None:
        try:
            args = loads(args_json or "{}")
        except JSONDecodeError:
            print(f"[GUI BRIDGE ERROR] invalid args_json for command={command}: {args_json}", flush=True)
            args = {}
        self._facade.handle_gui_command(command, args)
        self.update_state_from_facade()

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
        self.update_state_from_facade()
