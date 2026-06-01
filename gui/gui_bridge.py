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
    gameViewJsonChanged = Signal()
    renderResourcesJsonChanged = Signal()
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
        self._render_resources_loaded = False
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

    def _refresh_render_resources_from_facade(self, force: bool = False) -> bool:
        """Refresh heavyweight render resources only when explicitly needed.

        GameCanvas is fed by update_game_state_from_facade() at 50 ms.  The
        full GUI refresh may perform slower resource/control work; it must not
        rebuild render resources every tick or emit an older gameView after the
        game-only refresh has already delivered a newer frame.
        """
        if self._render_resources_loaded and not force:
            return False
        try:
            next_render_resources_json = dumps(self._facade.get_render_resources(), ensure_ascii=False)
        except Exception as exc:
            next_render_resources_json = dumps({"status": "error", "error": str(exc)}, ensure_ascii=False)
        self._render_resources_loaded = True
        if next_render_resources_json != self._render_resources_json:
            self._render_resources_json = next_render_resources_json
            self.renderResourcesJsonChanged.emit()
            return True
        return False

    def _action_requires_render_resource_refresh(self, action_id: str) -> bool:
        """Return True when an action mutates dynamic desktop-card context.

        TASK26 render resources contain mostly static layout/style data, but a
        few context blocks are hydrated from live control state:
        calibration/user/report panels read those blocks from renderResources.
        FIX11 cached renderResources to protect GameCanvas from stale full
        refresh frames, so these non-game actions must explicitly refresh the
        resource bundle after they change state.  Game actions stay on the
        dedicated 50 ms gameView/gameHud path.
        """
        text = str(action_id or "").strip().lower()
        if not text:
            return False
        return (
            text.startswith("calibration.")
            or text.startswith("user.")
            or text.startswith("report.")
            or text.startswith("diagnostics.")
        )

    @Slot()
    def refreshRenderResources(self) -> None:
        self._refresh_render_resources_from_facade(force=True)

    @Slot()
    def update_game_state_from_facade(self) -> None:
        """Refresh only the existing game view/HUD path for low-latency canvas updates.

        The full bridge refresh also rebuilds render resources and page/control JSON.
        That is too expensive to run at the GameCanvas feedback rate. This method
        deliberately reuses the existing facade.get_game_view()/get_game_hud()
        contract and only emits the existing gameView/gameHud signals.
        """
        next_game_hud_json = dumps(self._facade.get_game_hud(), ensure_ascii=False)
        next_game_view_json = dumps(self._facade.get_game_view(), ensure_ascii=False)
        changed = False
        if next_game_hud_json != self._game_hud_json:
            self._game_hud_json = next_game_hud_json
            self.gameHudJsonChanged.emit()
            changed = True
        if next_game_view_json != self._game_view_json:
            self._game_view_json = next_game_view_json
            self.gameViewJsonChanged.emit()
            changed = True

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

        # Do not emit stateChanged for the 50 ms game-only refresh. MinimalGui
        # listens to gameViewJsonChanged/gameHudJsonChanged and updates only
        # those lightweight objects; emitting stateChanged here would force a
        # full JSON pull/render-resource parse on every game frame.
        _ = changed

    def update_state_from_facade(self) -> None:
        next_app_state = dumps(self._facade.get_app_state())
        next_runtime_snapshot = dumps(self._facade.get_runtime_snapshot())
        next_session_state = dumps(self._facade.get_session_state())
        next_control_manifest_json = dumps(self._facade.get_control_manifest(), ensure_ascii=False)
        next_control_state_json = dumps(self._facade.get_control_state(), ensure_ascii=False)
        next_page_command_manifest_json = dumps(self._facade.get_page_command_manifest(), ensure_ascii=False)

        # Do not fetch or emit gameView/gameHud here.  This method can perform
        # heavier page/control/resource work and may complete later than the
        # dedicated 50 ms game refresh.  Emitting gameViewJsonChanged here can
        # overwrite a fresh frame with an older frame and creates the visible
        # 500-600 ms target/ring lag diagnosed in TASK26 GameCanvas.
        changed = self._refresh_render_resources_from_facade(force=False)
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

    @Property(str, notify=gameViewJsonChanged)
    def gameViewJson(self) -> str:
        return self._game_view_json

    @Property(str, notify=renderResourcesJsonChanged)
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
        self.update_game_state_from_facade()

    @Slot(str, str, result=str)
    def invokeAction(self, action_id: str, payload_json: str = "{}") -> str:
        try:
            payload = loads(payload_json or "{}")
        except JSONDecodeError:
            payload = {}
        result = self._facade.invoke_action(action_id, payload)
        self.update_state_from_facade()
        if self._action_requires_render_resource_refresh(action_id):
            self._refresh_render_resources_from_facade(force=True)
        self.update_game_state_from_facade()
        # Desktop card buttons depend on stateChanged to make MinimalGui pull fresh
        # control/session/runtime objects after an action. Some actions only update
        # last_command_result, which does not always change the app/runtime/session
        # JSON enough to trigger update_state_from_facade's normal changed path.
        self.stateChanged.emit()
        self.controlStateJsonChanged.emit()
        self.sessionStateChanged.emit()
        self.runtimeSnapshotChanged.emit()
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
        if self._action_requires_render_resource_refresh(command):
            self._refresh_render_resources_from_facade(force=True)
        self.update_game_state_from_facade()

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
        if event_type == "pointer_click":
            self.update_game_state_from_facade()
        else:
            self.update_state_from_facade()

    @Slot(str, result=str)
    def handleGamePointerClick(self, payload_json: str = "{}") -> str:
        try:
            payload = loads(payload_json or "{}")
        except JSONDecodeError:
            print(f"[GUI BRIDGE ERROR] invalid game pointer payload_json: {payload_json}", flush=True)
            payload = {}
        self._facade.handle_gui_event("pointer_click", payload)
        self.update_game_state_from_facade()
        result = dict(self._facade.last_event_result or {})
        result.setdefault("status", "accepted")
        result["game_view"] = self._facade.get_game_view()
        result["game_hud"] = self._facade.get_game_hud()
        return dumps(result, ensure_ascii=False)
