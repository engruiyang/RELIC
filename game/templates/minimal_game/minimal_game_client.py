from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from game.game_contracts import BehaviorSample, GameEntity, GameEvent, GameInputEvent, GameViewState, VisualEvent


@dataclass(slots=True)
class _Target:
    x: float = 0.5
    y: float = 0.5
    radius: float = 0.12


class MinimalGameClient:
    """可复制的最小游戏模板。

    队友通常只需要改：
    - manifest
    - _target 与 update() 中的状态机
    - handle_input() 的命中规则与事件类型
    - build_game_view() 的 entities/visual_events
    - collect_behavior_sample() 的统计指标
    """

    def __init__(self) -> None:
        self._game_id = "minimal_template"
        self._manifest: dict[str, Any] = {
            "game_id": self._game_id,
            "display_name": "Minimal Template Game",
            "version": "0.1.0",
            "supported_inputs": ["pointer_click"],
            "supported_entities": ["target"],
            "supported_effects": ["hit_flash"],
            "default_difficulty": "normal",
            "mouse_action_map": {"0": "target_primary", "1": "background", "2": "send_test_click"},
            "report_enabled": True,
        }
        self._target = _Target()
        self._frame_id = 0
        self._score = 0
        self._combo = 0
        self._completed = False
        self._started = False
        self._events: list[GameEvent] = []
        self._visual_events: list[VisualEvent] = []
        self._target_clicks = 0
        self._background_clicks = 0

    @property
    def game_id(self) -> str:
        return self._game_id

    @property
    def manifest(self) -> dict[str, Any]:
        return dict(self._manifest)

    def start(self, context: dict[str, Any]) -> None:
        _ = context
        self._score = 0
        self._combo = 0
        self._completed = False
        self._started = True
        self._events.clear()
        self._visual_events.clear()
        self._target_clicks = 0
        self._background_clicks = 0

    def stop(self, reason: str) -> None:
        _ = reason
        self._started = False
        self._completed = True

    def update(self, runtime_snapshot: dict[str, Any], dt_ms: int) -> None:
        _ = runtime_snapshot
        _ = dt_ms
        self._frame_id += 1

    def handle_input(self, game_input_event: GameInputEvent) -> None:
        if game_input_event.input_type != "pointer_click":
            return
        if not self._started:
            return
        hit = self._is_target_hit(game_input_event.x_norm, game_input_event.y_norm)
        if hit:
            self._target_clicks += 1
            self._score += 10
            self._combo += 1
            self._events.append(
                GameEvent(
                    schema_version="game_event.v1",
                    event_id=f"target_click_{self._frame_id}_{self._target_clicks}",
                    session_id=game_input_event.session_id,
                    game_id=self.game_id,
                    event_type="target_click",
                    created_at_ms=game_input_event.created_at_ms,
                    reportable=True,
                    payload={"x_norm": game_input_event.x_norm, "y_norm": game_input_event.y_norm},
                )
            )
            self._visual_events.append(
                VisualEvent(
                    event_id=f"fx_hit_{self._frame_id}_{self._target_clicks}",
                    kind="hit_flash",
                    target_id="target_main",
                    x=self._target.x,
                    y=self._target.y,
                    effect_key="fx.hit.flash.small",
                    style_key="fx_style.default",
                    intensity=1.0,
                    duration_ms=120,
                )
            )
            return

        self._background_clicks += 1
        self._combo = 0
        self._events.append(
            GameEvent(
                schema_version="game_event.v1",
                event_id=f"background_click_{self._frame_id}_{self._background_clicks}",
                session_id=game_input_event.session_id,
                game_id=self.game_id,
                event_type="background_click",
                created_at_ms=game_input_event.created_at_ms,
                reportable=True,
                payload={"x_norm": game_input_event.x_norm, "y_norm": game_input_event.y_norm},
            )
        )

    def build_game_view(self) -> GameViewState:
        entities = [
            GameEntity(
                id="target_main",
                kind="target",
                role="primary",
                x=self._target.x,
                y=self._target.y,
                radius=self._target.radius,
                state="active",
                style_key="target_style.default",
                asset_key="target.core.circle",
                interactive=True,
                hit_shape="circle",
                metadata={"note": "replace me for your game"},
            )
        ]
        events = list(self._visual_events)
        self._visual_events.clear()
        return GameViewState(
            game_id=self.game_id,
            view_version="game_view.v1",
            frame_id=self._frame_id,
            score=self._score,
            combo=self._combo,
            level=1,
            hud={"score": self._score, "combo": self._combo},
            entities=entities,
            visual_events=events,
            layout_hints={"canvas": "game_canvas", "theme": "default"},
        )

    def collect_game_events(self) -> list[GameEvent]:
        events = list(self._events)
        self._events.clear()
        return events

    def collect_behavior_sample(self) -> BehaviorSample:
        actions = self._target_clicks + self._background_clicks
        accuracy = 0.0 if actions == 0 else self._target_clicks / actions
        false_action = 0.0 if actions == 0 else self._background_clicks / actions
        return BehaviorSample(
            window_ms=1000,
            target_count=max(1, self._target_clicks),
            correct_count=self._target_clicks,
            omission_count=0,
            false_action_count=self._background_clicks,
            action_count=actions,
            rt_samples_ms=[],
            accuracy=accuracy,
            omission=0.0,
            false_action=false_action,
            rt_stability=1.0,
            game_specific={"combo": self._combo},
        )

    def is_completed(self) -> bool:
        return self._completed

    def get_score(self) -> int:
        return self._score

    def _is_target_hit(self, x: float, y: float) -> bool:
        dx = x - self._target.x
        dy = y - self._target.y
        return dx * dx + dy * dy <= self._target.radius * self._target.radius
