from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from runtime.runtime_messages import GameEvent, RuntimeCommand, RuntimeSnapshotView


SnapshotCallback = Callable[[RuntimeSnapshotView], None]
CommandCallback = Callable[[RuntimeCommand], None]
GameEventCallback = Callable[[GameEvent], None]


class RuntimeAPI(ABC):
    @abstractmethod
    def publish_snapshot(self, snapshot_view: RuntimeSnapshotView) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_command(self, command: RuntimeCommand) -> None:
        raise NotImplementedError

    @abstractmethod
    def emit_game_event(self, game_event: GameEvent) -> None:
        raise NotImplementedError

    @abstractmethod
    def subscribe_snapshots(self, callback: SnapshotCallback) -> None:
        raise NotImplementedError

    @abstractmethod
    def subscribe_commands(self, game_id: str, callback: CommandCallback) -> None:
        raise NotImplementedError

    @abstractmethod
    def subscribe_game_events(self, callback: GameEventCallback) -> None:
        raise NotImplementedError
