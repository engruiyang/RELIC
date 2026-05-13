from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from game.game_view_state import GameViewState
from runtime.runtime_messages import GameEvent, RuntimeCommand, RuntimeSnapshotView


@dataclass(slots=True)
class FakeGameConfig:
    emit_every_n_snapshots: int = 1
    behavior_window_ms: int = 1000
    max_duration_sec: int = 60


class FakeGameClient:
    game_id = "fake_game"

    def __init__(self, config: FakeGameConfig | None = None):
        self.config = config or FakeGameConfig()
        self.session_id: str | None = None
        self.status = "stopped"
        self.score = 0.0
        self.combo = 0
        self.level = 1
        self.tick_count = 0
        self.last_control_state: str | None = None
        self.last_quality_state: str | None = None
        self.last_fi_smoothed: float | None = None
        self.last_sqi: float | None = None
        self._event_counter = 0
        self._last_now_ms = 0
        self._stable_streak = 0
        self._distracted_streak = 0

    def on_command(self, command: RuntimeCommand) -> list[GameEvent]:
        if command.command_type == "start_game":
            self.session_id = command.session_id
            self.status = "running"
            self.tick_count = 0
            return []
        if command.command_type == "pause_game" and self.status == "running":
            self.status = "paused"
            return []
        if command.command_type == "resume_game" and self.status == "paused":
            self.status = "running"
            return []
        if command.command_type == "stop_game":
            self.status = "stopped"
            return [self._event("game_completed", command.issued_at_ms, {"reason": "stopped", "final_score": self.score, "user_finished": False})]
        if command.command_type == "set_difficulty":
            req = command.payload.get("level")
            if isinstance(req, int):
                self.level = max(1, req)
            return []
        return []

    def on_snapshot(self, snapshot: RuntimeSnapshotView) -> list[GameEvent]:
        if self.status != "running" or self.session_id != snapshot.session_id:
            return []
        self.tick_count += 1
        self._last_now_ms = int(snapshot.now_ms or self.tick_count * 1000)
        self.last_control_state = snapshot.control_state
        self.last_quality_state = snapshot.quality_state
        self.last_fi_smoothed = snapshot.fi_smoothed
        self.last_sqi = snapshot.sqi

        score_delta = self._calc_score_delta(snapshot)
        self.score += score_delta
        if snapshot.control_state in {"STABLE_FOCUS", "HIGH_FOCUS"} and snapshot.fi_valid:
            self.combo += 1
            self._stable_streak += 1
            self._distracted_streak = 0
        else:
            self.combo = 0
            if snapshot.control_state == "DISTRACTED":
                self._distracted_streak += 1
            else:
                self._distracted_streak = 0
            self._stable_streak = 0

        events: list[GameEvent] = []
        if self.tick_count % self.config.emit_every_n_snapshots == 0:
            events.append(self._event("score_update", self._last_now_ms, {"score": self.score, "score_delta": score_delta, "combo": self.combo, "level": self.level}))

        if snapshot.control_state != "UNRELIABLE_SIGNAL":
            behavior_payload = self._build_behavior_sample(snapshot.control_state)
            if behavior_payload:
                events.append(self._event("behavior_sample", self._last_now_ms, behavior_payload))

        if self._stable_streak >= 3:
            events.append(self._event("difficulty_request", self._last_now_ms, {"requested_level": self.level + 1, "reason": "performance_high", "confidence": 0.8}))
            self._stable_streak = 0
        elif self._distracted_streak >= 3:
            events.append(self._event("difficulty_request", self._last_now_ms, {"requested_level": max(1, self.level - 1), "reason": "performance_low", "confidence": 0.7}))
            self._distracted_streak = 0

        if self.tick_count >= self.config.max_duration_sec:
            self.status = "stopped"
            events.append(self._event("game_completed", self._last_now_ms, {"reason": "completed", "final_score": self.score, "user_finished": True}))

        return events

    def get_view_state(self) -> GameViewState:
        return GameViewState(
            session_id=self.session_id,
            game_id=self.game_id,
            updated_at_ms=self._last_now_ms,
            score=self.score,
            combo=self.combo,
            level=self.level,
            status=self.status,
            control_state=self.last_control_state,
            quality_state=self.last_quality_state,
            feedback_hint="stable" if self.last_control_state in {"STABLE_FOCUS", "HIGH_FOCUS"} else "recover",
            hud={"fi": self.last_fi_smoothed, "sqi": self.last_sqi},
            entities=[],
            effects=[],
        )

    def _calc_score_delta(self, snapshot: RuntimeSnapshotView) -> float:
        delta = 0.0
        if snapshot.fi_valid and snapshot.control_state in {"STABLE_FOCUS", "HIGH_FOCUS"}:
            delta = 10.0
        elif snapshot.control_state == "DISTRACTED":
            delta = 2.0
        elif snapshot.control_state == "UNRELIABLE_SIGNAL":
            delta = 0.0
        if snapshot.quality_state == "warning":
            delta *= 0.5
        return delta

    def _build_behavior_sample(self, control_state: str | None) -> dict[str, Any] | None:
        if control_state in {"STABLE_FOCUS", "HIGH_FOCUS"}:
            accuracy, omission, false_action, rt_stability = 0.85, 0.05, 0.05, 0.80
        elif control_state == "DISTRACTED":
            accuracy, omission, false_action, rt_stability = 0.55, 0.30, 0.20, 0.45
        else:
            return None
        target_count = 20
        correct_count = int(round(target_count * accuracy))
        omission_count = int(round(target_count * omission))
        false_action_count = int(round(target_count * false_action))
        action_count = correct_count + false_action_count
        return {
            "window_ms": self.config.behavior_window_ms,
            "target_count": target_count,
            "correct_count": correct_count,
            "omission_count": omission_count,
            "false_action_count": false_action_count,
            "action_count": action_count,
            "rt_samples_ms": [320, 360, 410],
            "accuracy": accuracy,
            "omission": omission,
            "false_action": false_action,
            "rt_stability": rt_stability,
        }

    def _event(self, event_type: str, created_at_ms: int, payload: dict[str, Any]) -> GameEvent:
        self._event_counter += 1
        return GameEvent(event_id=f"fake_evt_{self._event_counter}", session_id=self.session_id or "", game_id=self.game_id, event_type=event_type, created_at_ms=created_at_ms, payload=payload)
