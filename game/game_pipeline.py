from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import json
import time

from core.control_state_estimator import ControlStateEstimator
from core.focus_estimator import FocusEstimator
from core.quality_gate import QualityGate
from data.data_center import DataCenter
from game.game_manager import GameManager
from relic_platform.platform_gateway import PlatformGateway
from runtime.local_runtime import LocalRuntime
from runtime.runtime_messages import RuntimeSnapshotView
from session.session_manager import SessionManager


@dataclass(slots=True)
class PipelineTickResult:
    tick: int
    session_id: str
    game_id: str
    timestamp_ms: int
    input: dict[str, Any]
    output: dict[str, Any]
    view_state: dict[str, Any] | None
    warnings: list[str]
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        json.dumps(data)
        return data


class GamePipelineRunner:
    def __init__(self, *, runtime: LocalRuntime, game_manager: GameManager, session_manager: SessionManager, session_id: str, user_id: str, game_id: str, max_events_per_tick: int = 100, pipeline_jsonl_path: str | None = None):
        self.runtime = runtime
        self.game_manager = game_manager
        self.session_manager = session_manager
        self.session_id = session_id
        self.user_id = user_id
        self.game_id = game_id
        self.max_events_per_tick = max_events_per_tick
        self.tick = 0
        self._prev_event_count = 0
        self._jsonl_fp = None
        if pipeline_jsonl_path:
            Path(pipeline_jsonl_path).parent.mkdir(parents=True, exist_ok=True)
            self._jsonl_fp = open(pipeline_jsonl_path, "w", encoding="utf-8")

    def process_snapshot(self, runtime_snapshot: dict[str, Any]) -> PipelineTickResult:
        self.tick += 1
        warnings: list[str] = []
        errors: list[str] = []
        if not runtime_snapshot:
            warnings.append("runtime_snapshot_missing")
            runtime_snapshot = {}

        snapshot = RuntimeSnapshotView(
            session_id=self.session_id,
            user_id=self.user_id,
            game_id=self.game_id,
            now_ms=runtime_snapshot.get("now_ms"),
            attention=runtime_snapshot.get("attention"),
            attention_age_ms=runtime_snapshot.get("attention_age_ms"),
            attention_fresh=runtime_snapshot.get("attention_fresh"),
            gyro_x=runtime_snapshot.get("gyro_x"),
            gyro_y=runtime_snapshot.get("gyro_y"),
            gyro_z=runtime_snapshot.get("gyro_z"),
            gyro_age_ms=runtime_snapshot.get("gyro_age_ms"),
            gyro_fresh=runtime_snapshot.get("gyro_fresh"),
            sqi=runtime_snapshot.get("sqi"),
            quality_state=runtime_snapshot.get("quality_state"),
            fi_raw=runtime_snapshot.get("fi_raw"),
            fi_smoothed=runtime_snapshot.get("fi_smoothed"),
            fi_valid=runtime_snapshot.get("fi_valid"),
            fi_confidence=runtime_snapshot.get("fi_confidence"),
            control_state=runtime_snapshot.get("control_state"),
            control_state_reason=runtime_snapshot.get("control_state_reason"),
            warning_flags=runtime_snapshot.get("warning_flags"),
            error_flags=runtime_snapshot.get("error_flags"),
            interval_ms=runtime_snapshot.get("interval_ms"),
            delta_ms=runtime_snapshot.get("delta_ms"),
            behavior_ready=runtime_snapshot.get("behavior_ready"),
        )
        self.runtime.publish_snapshot(snapshot)
        self.session_manager.record_runtime_snapshot(snapshot)

        all_events = self.game_manager.get_buffered_events()
        new_events = all_events[self._prev_event_count :]
        self._prev_event_count = len(all_events)
        rejected_event_count = max(0, len(new_events) - self.max_events_per_tick)
        if len(new_events) > self.max_events_per_tick:
            new_events = new_events[: self.max_events_per_tick]
            warnings.append("max_events_per_tick_exceeded")

        event_types = [e.event_type for e in new_events]
        view_state = self.game_manager.get_current_view_state()
        out = {
            "event_count": len(new_events),
            "event_types": event_types,
            "score_update_count": event_types.count("score_update"),
            "behavior_sample_count": event_types.count("behavior_sample"),
            "difficulty_request_count": event_types.count("difficulty_request"),
            "game_completed_count": event_types.count("game_completed"),
            "rejected_event_count": rejected_event_count,
            "score": None if not view_state else view_state.get("score"),
            "combo": None if not view_state else view_state.get("combo"),
            "level": None if not view_state else view_state.get("level"),
        }
        inp = {
            "runtime_snapshot_seen": bool(runtime_snapshot),
            "attention": snapshot.attention,
            "attention_age_ms": snapshot.attention_age_ms,
            "attention_fresh": snapshot.attention_fresh,
            "gyro_fresh": snapshot.gyro_fresh,
            "sqi": snapshot.sqi,
            "quality_state": snapshot.quality_state,
            "fi_smoothed": snapshot.fi_smoothed,
            "fi_valid": snapshot.fi_valid,
            "control_state": snapshot.control_state,
            "control_state_reason": snapshot.control_state_reason,
            "warning_flags": snapshot.warning_flags,
            "error_flags": snapshot.error_flags,
        }
        r = PipelineTickResult(self.tick, self.session_id, self.game_id, int(time.time() * 1000), inp, out, view_state, warnings, errors)
        if self._jsonl_fp:
            self._jsonl_fp.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")
            self._jsonl_fp.flush()
        return r

    def stop(self, reason: str = "pipeline_stop") -> None:
        self.game_manager.stop_game(issued_at_ms=int(time.time() * 1000))

    def close(self) -> None:
        if self._jsonl_fp:
            self._jsonl_fp.close(); self._jsonl_fp = None


class RuntimeSnapshotProvider:
    def next_snapshot(self, now_ms: int) -> dict[str, Any]:
        raise NotImplementedError


class MockSnapshotProvider(RuntimeSnapshotProvider):
    def __init__(self): self.i = 0
    def next_snapshot(self, now_ms: int) -> dict[str, Any]:
        states = ["STABLE_FOCUS", "HIGH_FOCUS", "DISTRACTED", "UNRELIABLE_SIGNAL"]
        c = states[self.i % len(states)]; self.i += 1
        return {"now_ms": now_ms, "attention": 60 + (self.i % 10), "attention_age_ms": 120, "attention_fresh": True, "gyro_fresh": True, "sqi": 0.9, "quality_state": "ok" if self.i % 3 else "warning", "fi_raw": 0.72, "fi_smoothed": 0.70, "fi_valid": True, "fi_confidence": 0.8, "control_state": c, "control_state_reason": "mock", "warning_flags": [], "error_flags": [], "delta_ms": 1000, "behavior_ready": True}


class LiveSnapshotProvider(RuntimeSnapshotProvider):
    def __init__(self, host: str, port: int):
        self.gateway = PlatformGateway(mode="live", host=host, port=port)
        self.data_center = DataCenter(); self.qg = QualityGate(); self.fe = FocusEstimator(); self.cs = ControlStateEstimator(); self.gateway.start()
    def next_snapshot(self, now_ms: int) -> dict[str, Any]:
        events = self.gateway.poll_raw_events(now_ms=now_ms)
        self.data_center.ingest_events(events, now_ms=now_ms)
        s = self.data_center.get_runtime_snapshot()
        gate = self.qg.evaluate(s, current_user=None, user_profile=None, bound_calibration_profile=None, warning_flags=s.get("warning_flags"), error_flags=s.get("error_flags"))
        self.data_center.apply_quality_gate(gate)
        s = self.data_center.get_runtime_snapshot()
        fi = self.fe.estimate(s, None, None); cs = self.cs.evaluate(s, fi, tick_ms=int(s.get("delta_ms") or 1000)); s.update(fi); s.update(cs)
        return {k: s.get(k) for k in ["now_ms","attention","attention_age_ms","attention_fresh","gyro_x","gyro_y","gyro_z","gyro_age_ms","gyro_fresh","sqi","quality_state","fi_raw","fi_smoothed","fi_valid","fi_confidence","control_state","control_state_reason","warning_flags","error_flags","delta_ms","behavior_ready"]}
    def close(self): self.gateway.stop()
