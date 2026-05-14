from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot
from typing import Any

from game.game_contracts import BehaviorSample, GameEntity, GameEvent, GameInputEvent, GameViewState, VisualEvent


@dataclass(slots=True)
class FakeClickGameClient:
    game_id: str = "fake_click_game"
    manifest: dict[str, Any] = field(default_factory=lambda: {"name": "Fake Click Game", "version": "14A", "supports": ["pointer_click"]})
    target_id: str = "fake_target_0"
    target_x: float = 0.5
    target_y: float = 0.5
    target_radius: float = 0.08
    mouse_action_map: dict[int, str] = field(default_factory=lambda: {0: "target_primary", 1: "background", 2: "send_test_click"})

    _started: bool = field(default=False, init=False)
    _completed: bool = field(default=False, init=False)
    _session_id: str = field(default="", init=False)
    _frame_id: int = field(default=0, init=False)
    _score: int = field(default=0, init=False)
    _combo: int = field(default=0, init=False)
    _event_seq: int = field(default=0, init=False)
    _pending_events: list[GameEvent] = field(default_factory=list, init=False)
    _pending_visual_events: list[VisualEvent] = field(default_factory=list, init=False)
    _target_count: int = field(default=0, init=False)
    _correct_count: int = field(default=0, init=False)
    _false_action_count: int = field(default=0, init=False)
    _rt_samples_ms: list[int] = field(default_factory=list, init=False)

    def start(self, context: dict[str, Any]) -> None:
        self._started = True
        self._completed = False
        self._session_id = str(context.get("session_id", ""))
        self._frame_id = 0
        self._score = 0
        self._combo = 0
        self._event_seq = 0
        self._pending_events.clear()
        self._pending_visual_events.clear()
        self._target_count = 0
        self._correct_count = 0
        self._false_action_count = 0
        self._rt_samples_ms = []

    def stop(self, reason: str) -> None:
        self._completed = True
        self._pending_events.append(self._make_event("game_completed", 0, True, {"reason": reason, "final_score": self._score}))

    def update(self, runtime_snapshot: dict[str, Any], dt_ms: int) -> None:
        self._frame_id += 1

    def handle_input(self, game_input_event: GameInputEvent) -> None:
        if not self._started or self._completed or game_input_event.input_type != "pointer_click":
            return
        self._target_count += 1
        action_name = self.mouse_action_map.get(game_input_event.button, "background")
        hit = self._is_hit(game_input_event.x_norm, game_input_event.y_norm)
        if hit:
            self._score += 1
            self._combo += 1
            self._correct_count += 1
            payload = {"target_id": self.target_id, "target_index": 0, "action_name": "target_primary", "hit": True, "pointer_x_norm": game_input_event.x_norm, "pointer_y_norm": game_input_event.y_norm}
            self._pending_events.append(self._make_event("target_click", game_input_event.created_at_ms, True, payload))
            self._pending_visual_events.append(VisualEvent(event_id=f"ve_{self._event_seq}", kind="pulse", target_id=self.target_id, x=self.target_x, y=self.target_y, effect_key="target_pulse", style_key="hit_positive", intensity=1.0, duration_ms=180, payload={"action_name": action_name}))
        else:
            self._combo = 0
            self._false_action_count += 1
            payload = {"target_index": 1, "action_name": "background", "hit": False, "pointer_x_norm": game_input_event.x_norm, "pointer_y_norm": game_input_event.y_norm}
            self._pending_events.append(self._make_event("background_click", game_input_event.created_at_ms, True, payload))

    def build_game_view(self) -> GameViewState:
        events, self._pending_visual_events = self._pending_visual_events, []
        return GameViewState(game_id=self.game_id, view_version="game_view.v1", frame_id=self._frame_id, score=self._score, combo=self._combo, level=1, hud={"score": self._score, "combo": self._combo}, entities=[GameEntity(id=self.target_id, kind="target", role="primary", x=self.target_x, y=self.target_y, radius=self.target_radius, state="active", style_key="target_default", asset_key="target_dot", interactive=True, hit_shape="circle", metadata={"target_index": 0})], visual_events=events, layout_hints={"canvas": "game_canvas", "theme": "default"})

    def collect_game_events(self) -> list[GameEvent]:
        events, self._pending_events = self._pending_events, []
        return events

    def collect_behavior_sample(self) -> BehaviorSample:
        action_count = self._correct_count + self._false_action_count
        omission_count = max(0, self._target_count - self._correct_count)
        accuracy = (self._correct_count / self._target_count) if self._target_count else 0.0
        omission = (omission_count / self._target_count) if self._target_count else 0.0
        false_action = (self._false_action_count / action_count) if action_count else 0.0
        return BehaviorSample(window_ms=1000, target_count=self._target_count, correct_count=self._correct_count, omission_count=omission_count, false_action_count=self._false_action_count, action_count=action_count, rt_samples_ms=list(self._rt_samples_ms), accuracy=accuracy, omission=omission, false_action=false_action, rt_stability=1.0 if len(self._rt_samples_ms) <= 1 else 0.5, game_specific={"combo": self._combo})

    def is_completed(self) -> bool:
        return self._completed

    def get_score(self) -> int:
        return self._score

    def _is_hit(self, x_norm: float, y_norm: float) -> bool:
        return hypot(x_norm - self.target_x, y_norm - self.target_y) <= self.target_radius

    def _make_event(self, event_type: str, created_at_ms: int, reportable: bool, payload: dict[str, Any]) -> GameEvent:
        self._event_seq += 1
        return GameEvent(schema_version="game_event.v1", event_id=f"fake_click_evt_{self._event_seq}", session_id=self._session_id, game_id=self.game_id, event_type=event_type, created_at_ms=created_at_ms, reportable=reportable, payload=payload)
