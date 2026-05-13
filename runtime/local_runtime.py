from __future__ import annotations

from collections import defaultdict

from runtime.runtime_api import CommandCallback, GameEventCallback, RuntimeAPI, SnapshotCallback
from runtime.runtime_messages import GameEvent, RuntimeCommand, RuntimeSnapshotView


class LocalRuntime(RuntimeAPI):
    def __init__(self) -> None:
        self._snapshot_subscribers: list[SnapshotCallback] = []
        self._command_subscribers: dict[str, list[CommandCallback]] = defaultdict(list)
        self._event_subscribers: list[GameEventCallback] = []

    def publish_snapshot(self, snapshot_view: RuntimeSnapshotView) -> None:
        for callback in self._snapshot_subscribers:
            callback(snapshot_view)

    def send_command(self, command: RuntimeCommand) -> None:
        for callback in self._command_subscribers.get(command.game_id, []):
            callback(command)

    def emit_game_event(self, game_event: GameEvent) -> None:
        for callback in self._event_subscribers:
            callback(game_event)

    def subscribe_snapshots(self, callback: SnapshotCallback) -> None:
        self._snapshot_subscribers.append(callback)

    def subscribe_commands(self, game_id: str, callback: CommandCallback) -> None:
        self._command_subscribers[game_id].append(callback)

    def subscribe_game_events(self, callback: GameEventCallback) -> None:
        self._event_subscribers.append(callback)
