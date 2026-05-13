from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from game.game_view_state import GameViewState
from runtime.runtime_messages import GameEvent, RuntimeCommand, RuntimeSnapshotView


ALLOWED_RENDERER_TYPES = {"headless", "pygame_future", "web_future", "platform_embed_future"}


class RendererAdapter(ABC):
    renderer_id: str
    renderer_type: str

    @abstractmethod
    def attach_runtime(self, runtime: Any) -> None: ...

    @abstractmethod
    def on_view_state(self, view_state: GameViewState) -> None: ...

    @abstractmethod
    def on_runtime_snapshot(self, snapshot: RuntimeSnapshotView) -> None: ...

    @abstractmethod
    def poll_input_events(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def close(self) -> None: ...


@dataclass(slots=True)
class HeadlessRendererStub(RendererAdapter):
    renderer_id: str = "headless_stub"
    renderer_type: str = "headless"
    runtime: Any = None
    last_view_state: dict[str, Any] | None = None
    last_snapshot: dict[str, Any] | None = None
    _input_events: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.renderer_type not in ALLOWED_RENDERER_TYPES:
            raise ValueError("unsupported renderer_type")

    def attach_runtime(self, runtime: Any) -> None:
        self.runtime = runtime

    def on_view_state(self, view_state: GameViewState) -> None:
        self.last_view_state = view_state.to_dict()

    def on_runtime_snapshot(self, snapshot: RuntimeSnapshotView) -> None:
        self.last_snapshot = snapshot.to_dict()

    def poll_input_events(self) -> list[dict[str, Any]]:
        out = list(self._input_events)
        self._input_events.clear()
        return out

    def close(self) -> None:
        self.runtime = None


def input_to_runtime_command(*, command_id: str, session_id: str, game_id: str, action: str, issued_at_ms: int, payload: dict[str, Any] | None = None) -> RuntimeCommand:
    allowed = {"pause_game", "resume_game", "stop_game", "set_feedback_mode"}
    if action not in allowed:
        raise ValueError("unsupported control action")
    return RuntimeCommand(command_id=command_id, session_id=session_id, game_id=game_id, command_type=action, issued_at_ms=issued_at_ms, payload=payload or {})


def input_to_user_action_event(*, event_id: str, session_id: str, game_id: str, created_at_ms: int, action_type: str, target_id: str, success: bool, rt_ms: int) -> GameEvent:
    payload = {"action_type": action_type, "target_id": target_id, "success": bool(success), "rt_ms": int(rt_ms)}
    return GameEvent(event_id=event_id, session_id=session_id, game_id=game_id, event_type="user_action", created_at_ms=created_at_ms, payload=payload)
