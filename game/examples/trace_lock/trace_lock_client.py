from __future__ import annotations

from dataclasses import dataclass
import logging
from statistics import mean
from typing import Any

from game.game_contracts import BehaviorSample, GameEntity, GameEvent, GameInputEvent, GameViewState, VisualEvent


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _LevelConfig:
    target_radius: float
    target_lifetime_ms: int
    movement_enabled: bool
    movement_speed: float
    burst_target_ratio: float


@dataclass(slots=True)
class _Target:
    target_id: str
    target_type: str
    x: float
    y: float
    radius: float
    spawned_at_ms: int
    expires_at_ms: int
    vx: float = 0.0
    vy: float = 0.0
    movement_type: str = "static"
    state: str = "active"


class TraceLockClient:
    game_id = "trace_lock"

    def __init__(self) -> None:
        self._manifest: dict[str, Any] = {
            "game_id": "trace_lock",
            "display_name": "TraceLock Protocol",
            "subtitle": "Data Trace Tracking Protocol",
            "vendor": "Qilin Logic",
            "version": "0.1.0",
            "supported_inputs": ["pointer_click"],
            "supported_entities": ["target", "focus_zone", "progress_ring", "timer_bar"],
            "supported_effects": ["trace_seal", "lock_failed", "trace_drop", "combo_popup", "level_up", "level_down"],
            "default_difficulty": 1,
            "mouse_action_map": {"0": "target_primary", "1": "background", "2": "target_omitted", "3": "trace_seal", "4": "lock_failed"},
        }
        self._level_cfg: dict[int, _LevelConfig] = {
            1: _LevelConfig(0.09, 1500, False, 0.0, 0.00),
            2: _LevelConfig(0.08, 1300, False, 0.0, 0.05),
            3: _LevelConfig(0.07, 1100, True, 0.00004, 0.10),
            4: _LevelConfig(0.06, 950, True, 0.00007, 0.15),
            5: _LevelConfig(0.05, 800, True, 0.00010, 0.20),
        }
        self._session_id = ""
        self._started = False
        self._completed = False
        self._frame_id = 0
        self._event_seq = 0
        self._fx_seq = 0
        self._target_seq = 0
        self._clock_ms = 0
        self._game_duration_ms = 30000
        self._score = 0
        self._combo = 0
        self._max_combo = 0
        self._level = 1
        self._last_level_change_ms = -10000
        self._last_difficulty_check_ms = 0
        self._hint = "locking"
        self._active_target: _Target | None = None
        self._events: list[GameEvent] = []
        self._visual_events: list[VisualEvent] = []
        self._target_count = 0
        self._correct_count = 0
        self._false_action_count = 0
        self._omission_count = 0
        self._action_count = 0
        self._rt_samples_ms: list[int] = []
        self._attention_stale_frames = 0
        self._gyro_unstable_frames = 0
        self._stable_focus_frames = 0
        self._trace_drop_count = 0
        self._trace_seal_count = 0
        self._snapshot: dict[str, Any] = {}
        self._level_change_count = 0
        self._debug_difficulty_level: int | None = None
        self._last_logged_movement_type = ""

    @property
    def manifest(self) -> dict[str, Any]:
        return dict(self._manifest)

    def start(self, context: dict[str, Any]) -> None:
        self._session_id = str(context.get("session_id", ""))
        self._level = int(context.get("difficulty", self._manifest["default_difficulty"]))
        if self._debug_difficulty_level is not None:
            self._level = self._debug_difficulty_level
        self._level = max(1, min(5, self._level))
        self._started = True
        self._completed = False
        self._frame_id = 0
        self._event_seq = 0
        self._fx_seq = 0
        self._target_seq = 0
        self._clock_ms = 0
        self._score = 0
        self._combo = 0
        self._max_combo = 0
        self._last_level_change_ms = -10000
        self._last_difficulty_check_ms = 0
        self._hint = "locking"
        self._events.clear()
        self._visual_events.clear()
        self._target_count = 0
        self._correct_count = 0
        self._false_action_count = 0
        self._omission_count = 0
        self._action_count = 0
        self._rt_samples_ms.clear()
        self._attention_stale_frames = 0
        self._gyro_unstable_frames = 0
        self._stable_focus_frames = 0
        self._trace_drop_count = 0
        self._trace_seal_count = 0
        self._snapshot = {}
        self._level_change_count = 0
        logger.info("[TRACELOCK] start session_id=%s level=%s override=%s", self._session_id, self._level, self._debug_difficulty_level)
        self._spawn_target()

    def stop(self, reason: str) -> None:
        self._started = False
        self._completed = True
        self._events.append(self._make_event("game_completed", self._clock_ms, False, {"reason": reason, "final_score": self._score}))
        logger.info("[TRACELOCK] completed score=%s accuracy=%.3f combo=%s", self._score, self.collect_behavior_sample().accuracy, self._combo)

    def update(self, runtime_snapshot: dict[str, Any], dt_ms: int) -> None:
        if not self._started:
            return
        step_ms = max(0, int(dt_ms))
        self._frame_id += 1
        self._clock_ms += step_ms
        self._snapshot = dict(runtime_snapshot or {})
        self._update_hint_and_live_stats()
        self._maybe_adjust_difficulty()
        self._move_target(step_ms)
        self._check_target_timeout()
        if self._clock_ms >= self._game_duration_ms and not self._completed:
            self._completed = True
            self._started = False
            self._events.append(self._make_event("game_completed", self._clock_ms, False, {"reason": "duration_elapsed", "final_score": self._score}))
            logger.info("[TRACELOCK] completed score=%s accuracy=%.3f combo=%s", self._score, self.collect_behavior_sample().accuracy, self._combo)

    def handle_input(self, game_input_event: GameInputEvent) -> None:
        if not self._started or self._completed:
            return
        if game_input_event.input_type != "pointer_click":
            return
        self._action_count += 1
        target = self._active_target
        if target and self._is_hit(game_input_event.x_norm, game_input_event.y_norm, target):
            rt_ms = max(0, game_input_event.created_at_ms - target.spawned_at_ms)
            self._combo += 1
            self._max_combo = max(self._max_combo, self._combo)
            score_delta = 1 if self._combo < 5 else (2 if self._combo < 10 else 3)
            self._score += score_delta
            self._correct_count += 1
            self._trace_seal_count += 1
            self._rt_samples_ms.append(rt_ms)
            self._events.append(self._make_event("target_click", game_input_event.created_at_ms, True, {"target_index": 0, "action_name": "target_primary", "hit": True, "reaction_time_ms": rt_ms, "combo": self._combo, "max_combo": self._max_combo, "score_delta": score_delta, "target_id": target.target_id, "target_type": target.target_type, "trace_sealed": True}))
            self._visual_events.append(self._make_fx("trace_seal", target, "tracelock.effect.trace_seal"))
            self._spawn_target()
            return

        self._combo = 0
        self._false_action_count += 1
        self._events.append(self._make_event("background_click", game_input_event.created_at_ms, True, {"target_index": 1, "action_name": "background", "hit": False}))
        if target:
            self._visual_events.append(self._make_fx("lock_failed", target, "tracelock.effect.lock_failed"))

    def build_game_view(self) -> GameViewState:
        target = self._active_target
        remaining_ratio = 0.0
        target_type = "marked_trace"
        target_time_left_ms = 0
        target_lifetime_ms = self._level_cfg[self._level].target_lifetime_ms
        target_entities: list[GameEntity] = []
        if target:
            target_time_left_ms = max(0, target.expires_at_ms - self._clock_ms)
            target_lifetime_ms = max(1, target.expires_at_ms - target.spawned_at_ms)
            remaining_ratio = max(0.0, min(1.0, target_time_left_ms / target_lifetime_ms))
            target_type = target.target_type
            key = self._asset_for_target(target.target_type)
            target_entities.append(GameEntity(id=target.target_id, kind="target", role="primary", x=target.x, y=target.y, radius=target.radius, state="active", style_key=key, asset_key=key, interactive=True, hit_shape="circle", metadata={"target_id": target.target_id, "target_type": target.target_type, "remaining_lifetime_ratio": remaining_ratio, "time_left_ms": target_time_left_ms, "target_lifetime_ms": target_lifetime_ms, "movement_type": target.movement_type, "level": self._level}))
            target_entities.append(GameEntity(id=f"ring_{target.target_id}", kind="progress_ring", role="lock_progress", x=target.x, y=target.y, radius=target.radius * 1.25, state="active", style_key="tracelock.progress_ring.default", asset_key="tracelock.progress_ring.default", interactive=False, hit_shape="circle", metadata={"progress": remaining_ratio, "time_left_ms": target_time_left_ms, "target_lifetime_ms": target_lifetime_ms}))

        pressure = "high" if remaining_ratio < 0.25 else ("medium" if remaining_ratio < 0.6 else "low")
        score_multiplier = 1 if self._combo < 5 else (2 if self._combo < 10 else 3)
        entities = target_entities + [
            GameEntity(id="focus_zone", kind="focus_zone", role="lock_area", x=0.5, y=0.5, radius=0.42, state="active", style_key="tracelock.focus_zone.default", asset_key="tracelock.focus_zone.default", interactive=False, hit_shape="circle", metadata={}),
            GameEntity(id="round_timer", kind="timer_bar", role="round_timer", x=0.5, y=0.04, radius=0.0, state="active", style_key="tracelock.timer.round", asset_key="tracelock.timer.round", interactive=False, hit_shape="rect", metadata={"progress": max(0.0, min(1.0, (self._game_duration_ms - self._clock_ms) / self._game_duration_ms))}),
        ]
        visual_events = [v for v in self._visual_events]
        self._visual_events.clear()
        sample = self.collect_behavior_sample()
        return GameViewState(game_id=self.game_id, view_version="game_view.v1", frame_id=self._frame_id, score=self._score, combo=self._combo, level=self._level, hud={"score": self._score, "combo": self._combo, "max_combo": self._max_combo, "score_multiplier": score_multiplier, "level": self._level, "load_tier": self._level, "time_left_ms": max(0, self._game_duration_ms - self._clock_ms), "hint": self._hint, "attention_fresh": bool(self._snapshot.get("attention_fresh", True)), "gyro_fresh": bool(self._snapshot.get("gyro_fresh", True)), "stream_alive": bool(self._snapshot.get("stream_alive", True)), "target_time_left_ms": target_time_left_ms, "target_lifetime_ms": target_lifetime_ms, "target_pressure_level": pressure, "target_type": target_type, "movement_type": target.movement_type if target else "n/a", "remaining_lifetime_ratio": remaining_ratio, "protocol_name": "TraceLock Protocol", "vendor": "Qilin Logic", "target_count": self._target_count, "correct_count": self._correct_count, "omission_count": self._omission_count, "false_action_count": self._false_action_count, "accuracy": sample.accuracy, "omission": sample.omission, "false_action": sample.false_action, "rt_stability": sample.rt_stability}, entities=entities, visual_events=visual_events, layout_hints={"canvas": "game_canvas", "render_mode": "contract_only"})

    def collect_game_events(self) -> list[GameEvent]:
        out = list(self._events)
        self._events.clear()
        return out

    def collect_behavior_sample(self) -> BehaviorSample:
        target_count = max(1, self._target_count)
        accuracy = self._correct_count / target_count
        omission = self._omission_count / target_count
        false_action = self._false_action_count / max(1, self._action_count)
        rtv = self._rtv()
        rt_stability = max(0.0, min(1.0, 1.0 - min(1.0, rtv / 400.0)))
        return BehaviorSample(window_ms=self._game_duration_ms, target_count=self._target_count, correct_count=self._correct_count, omission_count=self._omission_count, false_action_count=self._false_action_count, action_count=self._action_count, rt_samples_ms=list(self._rt_samples_ms), accuracy=accuracy, omission=omission, false_action=false_action, rt_stability=rt_stability, game_specific={"combo": self._combo, "max_combo": self._max_combo, "level": self._level, "level_change_count": self._level_change_count, "mean_reaction_time_ms": float(mean(self._rt_samples_ms)) if self._rt_samples_ms else 0.0, "rtv": rtv, "attention_stale_frames": self._attention_stale_frames, "gyro_unstable_frames": self._gyro_unstable_frames, "stable_focus_frames": self._stable_focus_frames, "trace_drop_count": self._trace_drop_count, "trace_seal_count": self._trace_seal_count})

    def is_completed(self) -> bool:
        return self._completed

    def get_score(self) -> int:
        return self._score

    def _spawn_target(self) -> None:
        cfg = self._level_cfg[self._level]
        self._target_seq += 1
        seed = self._target_seq
        x = 0.2 + ((seed * 37) % 61) / 100.0
        y = 0.2 + ((seed * 53) % 61) / 100.0
        target_type = "burst_trace" if (seed % 100) < int(cfg.burst_target_ratio * 100) else "marked_trace"
        if cfg.movement_enabled and seed % 11 == 0:
            target_type = "unstable_trace"
        movement_type = "static" if self._level <= 2 else ("drift" if self._level == 3 else ("linear" if self._level == 4 else "burst"))
        speed = cfg.movement_speed
        vx = speed
        vy = speed * (0.7 if movement_type == "drift" else (1.0 if movement_type == "linear" else 1.4))
        if seed % 2 == 0:
            vx = -vx
        if seed % 3 == 0:
            vy = -vy
        self._active_target = _Target(target_id=f"trace_{self._target_seq}", target_type=target_type, x=max(0.1, min(0.9, x)), y=max(0.12, min(0.9, y)), radius=cfg.target_radius, spawned_at_ms=self._clock_ms, expires_at_ms=self._clock_ms + cfg.target_lifetime_ms, vx=vx, vy=vy, movement_type=movement_type)
        self._target_count += 1
        logger.info("[TRACELOCK] spawn target_id=%s level=%s movement=%s type=%s lifetime_ms=%s", self._active_target.target_id, self._level, movement_type, target_type, cfg.target_lifetime_ms)
        if movement_type != self._last_logged_movement_type:
            logger.info("[TRACELOCK] movement_changed old=%s new=%s level=%s", self._last_logged_movement_type or "n/a", movement_type, self._level)
            self._last_logged_movement_type = movement_type

    def _move_target(self, dt_ms: int) -> None:
        t = self._active_target
        if not t or t.movement_type == "static":
            return
        capped_dt = min(dt_ms, 120)
        max_step = 0.03
        dx = max(-max_step, min(max_step, t.vx * capped_dt))
        dy = max(-max_step, min(max_step, t.vy * capped_dt))
        t.x += dx
        t.y += dy
        if t.x < 0.08:
            t.x = 0.08
            t.vx = abs(t.vx)
        elif t.x > 0.92:
            t.x = 0.92
            t.vx = -abs(t.vx)
        if t.y < 0.08:
            t.y = 0.08
            t.vy = abs(t.vy)
        elif t.y > 0.92:
            t.y = 0.92
            t.vy = -abs(t.vy)

    def _check_target_timeout(self) -> None:
        target = self._active_target
        if not target:
            return
        if self._clock_ms < target.expires_at_ms:
            return
        self._combo = 0
        self._omission_count += 1
        self._trace_drop_count += 1
        self._events.append(self._make_event("target_omitted", self._clock_ms, False, {"omission": True, "target_id": target.target_id, "trace_drop": True}))
        self._visual_events.append(self._make_fx("trace_drop", target, "tracelock.effect.trace_drop"))
        self._spawn_target()

    def _update_hint_and_live_stats(self) -> None:
        s = self._snapshot
        if s.get("error_flags"):
            self._hint = "signal_error"
        elif not bool(s.get("gyro_fresh", True)):
            self._hint = "gyro_link_unstable"
        elif not bool(s.get("attention_fresh", True)):
            self._hint = "focus_sync_pending"
        elif s.get("control_state") == "FATIGUED":
            self._hint = "rest_suggested"
        elif s.get("control_state") == "DISTRACTED":
            self._hint = "refocus"
        elif s.get("control_state") == "HIGH_FOCUS":
            self._hint = "trace_predict_stable"
        else:
            self._hint = "locking"
        if not bool(s.get("attention_fresh", True)):
            self._attention_stale_frames += 1
        if not bool(s.get("gyro_fresh", True)):
            self._gyro_unstable_frames += 1
        if s.get("control_state") == "HIGH_FOCUS":
            self._stable_focus_frames += 1

    def _maybe_adjust_difficulty(self) -> None:
        if self._debug_difficulty_level is not None:
            self._level = self._debug_difficulty_level
            return
        if self._clock_ms - self._last_difficulty_check_ms < 5000:
            return
        self._last_difficulty_check_ms = self._clock_ms
        sample = self.collect_behavior_sample()
        state = str(self._snapshot.get("control_state", ""))
        gyro_ok = bool(self._snapshot.get("gyro_fresh", True))
        upgrade_allowed = state not in {"DISTRACTED", "FATIGUED"} and gyro_ok
        high_focus = state == "HIGH_FOCUS"
        up = upgrade_allowed and high_focus and sample.accuracy >= 0.85 and sample.false_action <= 0.10 and sample.omission <= 0.10 and sample.rt_stability >= 0.70
        down = sample.accuracy < 0.60 or sample.false_action > 0.25 or sample.omission > 0.25
        if self._clock_ms - self._last_level_change_ms < 10000:
            return
        old = self._level
        if up and self._level < 5:
            self._level += 1
        elif down and self._level > 1:
            self._level -= 1
        if old != self._level:
            self._level_change_count += 1
            self._last_level_change_ms = self._clock_ms
            self._events.append(self._make_event("level_changed", self._clock_ms, False, {"old_level": old, "new_level": self._level}))
            logger.info("[TRACELOCK] level_changed old=%s new=%s reason=auto_dda", old, self._level)

    def set_debug_difficulty(self, level: int | None) -> None:
        if level is None:
            self._debug_difficulty_level = None
            logger.info("[TRACELOCK] debug_difficulty level=auto")
            return
        clamped = max(1, min(5, int(level)))
        self._debug_difficulty_level = clamped
        self._level = clamped
        if self._started:
            self._spawn_target()
        logger.info("[TRACELOCK] debug_difficulty level=%s", clamped)

    def _make_event(self, event_type: str, created_at_ms: int, reportable: bool, payload: dict[str, Any]) -> GameEvent:
        self._event_seq += 1
        return GameEvent("game_event.v1", f"trace_evt_{self._event_seq}", self._session_id, self.game_id, event_type, int(created_at_ms), reportable, payload)

    def _make_fx(self, kind: str, target: _Target, effect_key: str) -> VisualEvent:
        self._fx_seq += 1
        return VisualEvent(event_id=f"trace_fx_{self._fx_seq}", kind=kind, target_id=target.target_id, x=target.x, y=target.y, effect_key=effect_key, style_key=effect_key, intensity=1.0, duration_ms=220, payload={"target_type": target.target_type})

    def _is_hit(self, x: float, y: float, target: _Target) -> bool:
        dx = x - target.x
        dy = y - target.y
        return dx * dx + dy * dy <= target.radius * target.radius

    def _asset_for_target(self, target_type: str) -> str:
        return {"marked_trace": "tracelock.target.marked_trace", "burst_trace": "tracelock.target.burst_trace", "unstable_trace": "tracelock.target.unstable_trace"}.get(target_type, "tracelock.target.marked_trace")

    def _rtv(self) -> float:
        if len(self._rt_samples_ms) <= 1:
            return 0.0
        m = mean(self._rt_samples_ms)
        variance = mean([(x - m) ** 2 for x in self._rt_samples_ms])
        return float(variance ** 0.5)
