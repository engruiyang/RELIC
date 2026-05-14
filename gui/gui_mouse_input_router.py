from __future__ import annotations

from copy import deepcopy
from time import time
from typing import Any

from game.fake_click_game_client import FakeClickGameClient
from game.game_contracts import GameInputEvent
from .game_event_platform_adapter import GameEventPlatformAdapter


class GuiMouseInputRouter:
    def __init__(self, game_id: str = "fake_game") -> None:
        self.game_id = game_id
        self._client = FakeClickGameClient()
        self._started = False
        self._event_seq = 0
        self.last_game_input: GameInputEvent | None = None
        self.last_game_event: dict[str, Any] = {}
        self.last_game_view_summary: dict[str, Any] = {}
        self.game_event_count = 0
        self._platform_adapter = GameEventPlatformAdapter()
        self._active_session_id: str | None = None

    def route_gui_event(self, *, event_type: str, payload: dict[str, Any], session_id: str | None) -> dict[str, Any]:
        x_norm = float(payload.get("x_norm", 0.0))
        y_norm = float(payload.get("y_norm", 0.0))
        if not (0.0 <= x_norm <= 1.0 and 0.0 <= y_norm <= 1.0):
            return {"result": "ignored", "status": "ignored", "reason": "invalid_pointer_range", "source": "core_control"}

        active_session_id = session_id or "gui_mouse_debug_session"
        if (not self._started) or (self._active_session_id != active_session_id):
            if self._started:
                self._client.stop("session_context_switched")
                self._client.collect_game_events()
            self._client.start({"session_id": active_session_id, "game_id": self.game_id})
            self._started = True
            self._active_session_id = active_session_id

        game_input = GameInputEvent(
            event_id=self._next_event_id(),
            session_id=active_session_id,
            game_id=str(payload.get("game_id") or self.game_id),
            input_type="pointer_click",
            created_at_ms=int(time() * 1000),
            source=str(payload.get("source") or "minimal_game_canvas"),
            x_norm=x_norm,
            y_norm=y_norm,
            button=self._normalize_button(payload.get("button")),
            raw_event_type=event_type,
            debug_hit=payload.get("hit"),
            payload=deepcopy(payload),
        )
        self.last_game_input = game_input
        print(f"[GAME INPUT] type={game_input.input_type} x={game_input.x_norm:.3f} y={game_input.y_norm:.3f} session_id={game_input.session_id}", flush=True)

        self._client.handle_input(game_input)
        events = self._client.collect_game_events()
        last_platform_result = "idle"
        for evt in events:
            self.last_game_event = evt.to_dict()
            self.game_event_count += 1
            e_payload = evt.payload or {}
            print(
                f"[GAME EVENT] event_type={evt.event_type} target_index={e_payload.get('target_index')} action={e_payload.get('action_name')} hit={e_payload.get('hit')}",
                flush=True,
            )
            platform_res = self._platform_adapter.process_game_event(self.last_game_event, allow_mock=session_id is not None)
            last_platform_result = str(platform_res.get("platform_result") or last_platform_result)
        view = self._client.build_game_view()
        self.last_game_view_summary = {
            "score": view.score,
            "combo": view.combo,
            "entity_count": len(view.entities),
            "visual_event_count": len(view.visual_events),
        }
        result = "game_event_recorded_no_session_context" if session_id is None else last_platform_result
        if result in {"idle", "skipped_not_reportable", "skipped_unmapped_event_type"}:
            result = "recorded_only"

        return {
            "result": result,
            "status": "accepted",
            "reason": result,
            "source": "core_control",
            "event_type": event_type,
            "game_input": game_input.to_dict(),
            "game_event_count": self.game_event_count,
            "last_game_event": dict(self.last_game_event),
            "last_game_view_summary": dict(self.last_game_view_summary),
            "no_session_context": session_id is None,
            "platform_message_count": self._platform_adapter.platform_message_count,
            "last_platform_message": dict(self._platform_adapter.last_platform_message),
            "last_platform_result": self._platform_adapter.last_platform_result,
        }

    def _next_event_id(self) -> str:
        self._event_seq += 1
        return f"gui_game_input_{self._event_seq}"

    @staticmethod
    def _normalize_button(button: Any) -> int:
        if isinstance(button, int):
            return button
        if isinstance(button, str):
            lowered = button.lower()
            if lowered == "left":
                return 0
            if lowered == "right":
                return 1
            if lowered == "middle":
                return 2
        return 0
