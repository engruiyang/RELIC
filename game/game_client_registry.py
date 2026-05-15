from __future__ import annotations

from typing import Callable

from game.fake_click_game_client import FakeClickGameClient
from game.game_contracts import GameClientPort
from game.examples.trace_lock.trace_lock_client import TraceLockClient


def _make_fake_game(game_id: str) -> GameClientPort:
    return FakeClickGameClient(game_id=game_id)


def _make_trace_lock(game_id: str) -> GameClientPort:
    _ = game_id
    return TraceLockClient()


_REGISTRY: dict[str, Callable[[str], GameClientPort]] = {
    "fake_game": _make_fake_game,
    "trace_lock": _make_trace_lock,
}


def create_game_client(game_id: str) -> GameClientPort:
    creator = _REGISTRY.get(game_id)
    if creator is None:
        raise ValueError(f"unsupported game_id: {game_id}")
    return creator(game_id)


def supported_game_ids() -> list[str]:
    return sorted(_REGISTRY.keys())
