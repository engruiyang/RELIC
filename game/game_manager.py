from __future__ import annotations

from game.fake_game_client import FakeGameClient
from game.game_manifest import GameManifest
from game.game_view_state import GameViewState
from game.renderer_adapter import RendererAdapter
from runtime.local_runtime import LocalRuntime
from runtime.runtime_messages import GameEvent, RuntimeCommand, RuntimeSnapshotView


class GameManager:
    def __init__(self, runtime: LocalRuntime, session_manager: object | None = None):
        self.runtime = runtime
        self.session_manager = session_manager
        self._manifests: dict[str, GameManifest] = {}
        self._clients: dict[str, FakeGameClient] = {}
        self._current_game_id: str | None = None
        self._current_session_id: str | None = None
        self._event_buffer: list[GameEvent] = []
        self._runtime_subscribed = False
        self._renderers: list[RendererAdapter] = []

    def register_game(self, manifest: GameManifest, client: FakeGameClient) -> None:
        self._manifests[manifest.game_id] = manifest
        self._clients[manifest.game_id] = client
        self.runtime.subscribe_commands(manifest.game_id, self._on_command)
        if not self._runtime_subscribed:
            self.runtime.subscribe_snapshots(self._on_snapshot)
            self._runtime_subscribed = True

    def list_games(self) -> list[dict]:
        return [m.to_dict() for m in self._manifests.values()]

    def select_game(self, game_id: str) -> bool:
        if game_id not in self._manifests:
            return False
        self._current_game_id = game_id
        return True

    def start_game(self, session_id: str, issued_at_ms: int = 0) -> bool:
        if not self._current_game_id:
            return False
        self._current_session_id = session_id
        cmd = RuntimeCommand(command_id="gm_start", session_id=session_id, game_id=self._current_game_id, command_type="start_game", issued_at_ms=issued_at_ms, payload={})
        self.runtime.send_command(cmd)
        return True

    def stop_game(self, issued_at_ms: int = 0) -> bool:
        if not self._current_game_id or not self._current_session_id:
            return False
        cmd = RuntimeCommand(command_id="gm_stop", session_id=self._current_session_id, game_id=self._current_game_id, command_type="stop_game", issued_at_ms=issued_at_ms, payload={})
        self.runtime.send_command(cmd)
        return True

    def send_command(self, command: RuntimeCommand) -> None:
        self.runtime.send_command(command)

    def get_current_view_state(self) -> dict | None:
        client = self._current_client()
        if not client:
            return None
        return client.get_view_state().to_dict()

    def get_buffered_events(self) -> list[GameEvent]:
        return list(self._event_buffer)

    def register_renderer(self, renderer: RendererAdapter) -> None:
        renderer.attach_runtime(self.runtime)
        self._renderers.append(renderer)

    def _on_command(self, command: RuntimeCommand) -> None:
        client = self._clients.get(command.game_id)
        if not client:
            return
        events = client.on_command(command)
        for e in events:
            self._handle_event(e)

    def _on_snapshot(self, snapshot: RuntimeSnapshotView) -> None:
        client = self._current_client()
        if not client:
            return
        for event in client.on_snapshot(snapshot):
            self._handle_event(event)
        self._notify_renderers(client.get_view_state(), snapshot)

    def _current_client(self) -> FakeGameClient | None:
        if not self._current_game_id:
            return None
        return self._clients.get(self._current_game_id)

    def _handle_event(self, event: GameEvent) -> None:
        if self._current_session_id and event.session_id != self._current_session_id:
            return
        if self._current_game_id and event.game_id != self._current_game_id:
            return
        self._event_buffer.append(event)
        if self.session_manager and getattr(self.session_manager, "has_active_session", lambda: False)():
            self.session_manager.record_game_event(event)

    def _notify_renderers(self, view_state: GameViewState, snapshot: RuntimeSnapshotView) -> None:
        for renderer in self._renderers:
            renderer.on_view_state(view_state)
            renderer.on_runtime_snapshot(snapshot)
