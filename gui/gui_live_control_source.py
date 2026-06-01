from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from storage.sqlite_store import SqliteStore
from storage.session_report_writer import write_session_report

from game.game_client_registry import create_game_client
from game.game_contracts import GameInputEvent
from .game_event_platform_adapter import GameEventPlatformAdapter
from .gui_live_readonly_source import GuiLiveReadonlySource


class GuiLiveControlSource:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000, poll_interval_sec: float = 0.05, live_source: GuiLiveReadonlySource | None = None, user_id: str = "demo_user", game_id: str = "fake_game") -> None:
        self.user_id = user_id
        self.game_id = game_id
        self.poll_interval_sec = poll_interval_sec
        self._live_source = live_source or GuiLiveReadonlySource(host=host, port=port, poll_interval_sec=poll_interval_sec)
        self._client = create_game_client(game_id)
        self._platform_adapter = GameEventPlatformAdapter()
        self._lock = threading.Lock()
        self._tick_thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._event_seq = 0

        self.live_debug_session_id: str | None = None
        self.training_session_id: str | None = None
        self.session_type: str = ""
        self.interaction_enabled = False
        self.session_type = ""
        self._store = SqliteStore("data/relic_local.db")
        self._training_context: dict[str, Any] = {}
        self._training_samples: list[dict[str, Any]] = []
        self._training_runtime: list[dict[str, Any]] = []
        self._training_events: list[dict[str, Any]] = []
        self.game_update_count = 0
        self.last_runtime_attention: int | None = None
        self.last_runtime_attention_fresh = False
        self.last_runtime_gyro_fresh = False
        self.last_game_event: dict[str, Any] = {}
        self.last_game_action_name = ""
        self.last_game_target_index: int | None = None
        self.game_event_count = 0
        self.last_game_view: dict[str, Any] = asdict(self._client.build_game_view())
        self.last_report_path = ""
        self.last_training_status = "idle"
        self.last_session_id = ""
        self._debug_difficulty_level: int | None = None
        self._difficulty_mode = "auto"
        self._session_start_game_event_count = 0
        self._training_duration_ms = 180000
        self._live_debug_duration_ms = 60000
        self._training_window_ms = 5000
        self._training_windows: list[dict[str, Any]] = []
        self._difficulty_decisions: list[dict[str, Any]] = []
        self._dda_state: dict[str, Any] = {}
        self._last_behavior_snapshot_ms = 0
        self._behavior_snapshot_interval_ms = 1000
        self._last_tick_started_wall_ms = 0
        self._last_tick_built_wall_ms = 0
        self._last_tick_elapsed_ms = 0
        self._last_tick_seq = 0

    def start(self) -> None:
        self._live_source.start()
        self._stop.clear()
        self._tick_thread = threading.Thread(target=self._tick_loop, daemon=True, name="GuiLiveControlTick")
        self._tick_thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._tick_thread and self._tick_thread.is_alive():
            self._tick_thread.join(timeout=1.0)
        self._live_source.stop()

    def _as_float_or_none(self, value: Any) -> float | None:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _clip(self, value: float, lo: float = 0.0, hi: float = 100.0) -> float:
        return max(lo, min(hi, float(value)))

    def _current_calibration_profile(self) -> dict[str, Any]:
        calib = self._training_context.get("calibration_profile")
        return dict(calib) if isinstance(calib, dict) else {}

    def _derive_control_state_from_fi(self, fi_value: float | None) -> str:
        if fi_value is None:
            return "UNKNOWN"
        if fi_value >= 80:
            return "HIGH_FOCUS"
        if fi_value >= 60:
            return "STABLE_FOCUS"
        if fi_value >= 40:
            return "DISTRACTED"
        return "FATIGUED"

    def _resolve_runtime_fi(self, runtime: dict[str, Any], behavior_sample: dict[str, Any] | None = None, calibration_profile: dict[str, Any] | None = None) -> dict[str, Any]:
        attention = self._as_float_or_none(runtime.get("attention"))
        if attention is None:
            attention = self._as_float_or_none(runtime.get("last_runtime_attention"))
        attention_age_ms = self._as_float_or_none(runtime.get("attention_age_ms"))
        attention_fresh = bool(runtime.get("attention_fresh", runtime.get("last_runtime_attention_fresh", attention is not None)))
        stream_alive = bool(runtime.get("stream_alive", True))
        error_flags = list(runtime.get("error_flags") or [])
        quality_state = str(runtime.get("quality_state") or "").lower()
        sqi = self._as_float_or_none(runtime.get("sqi"))

        candidate_order = ("fi_smoothed", "focus_index", "fi_raw", "fi")
        placeholder_zero_detected = False
        placeholder_zero_source = ""

        for key in candidate_order:
            val = self._as_float_or_none(runtime.get(key))
            if val is None:
                continue
            if val == 0.0:
                looks_placeholder = (
                    attention is not None
                    and (attention_fresh or (attention_age_ms is not None and attention_age_ms <= 1500))
                    and stream_alive
                    and not error_flags
                    and ((sqi is not None and sqi >= 0.5) or quality_state in {"ok", "warning", "valid"} or attention_fresh)
                )
                if looks_placeholder:
                    placeholder_zero_detected = True
                    placeholder_zero_source = key
                    continue
                if attention is None or not stream_alive or error_flags:
                    continue
            return {"fi": self._clip(val), "fi_source": key, "fi_unavailable_reason": "", "fi_valid": True, "fi_provisional": False, "fi_placeholder_zero_detected": placeholder_zero_detected, "fi_placeholder_zero_source": placeholder_zero_source}

        if attention is None or not stream_alive or error_flags:
            return {"fi": None, "fi_source": "unavailable", "fi_unavailable_reason": "attention_or_stream_invalid", "fi_valid": False, "fi_provisional": False, "fi_placeholder_zero_detected": placeholder_zero_detected, "fi_placeholder_zero_source": placeholder_zero_source}

        calib = calibration_profile if isinstance(calibration_profile, dict) else self._current_calibration_profile()
        baseline = self._as_float_or_none(calib.get("attention_baseline")) if isinstance(calib, dict) else None
        std = self._as_float_or_none(calib.get("attention_std")) if isinstance(calib, dict) else None
        if baseline is not None:
            z = (attention - baseline) / max(std or 1.0, 1.0)
            s_eeg = max(0.0, min(1.0, 0.5 + z / 4.0))
            fi_source = "calibration_attention_behavior_provisional"
        else:
            s_eeg = max(0.0, min(1.0, attention / 100.0))
            fi_source = "attention_behavior_provisional"

        gyro_fresh = bool(runtime.get("gyro_fresh", runtime.get("last_runtime_gyro_fresh", True)))
        gyro_error = any(flag in {"gyro_lost", "gyro_unstable"} for flag in error_flags)
        s_imu = 0.2 if gyro_error else (1.0 if gyro_fresh else 0.5)

        behavior = behavior_sample or {}
        acc = self._as_float_or_none(behavior.get("accuracy"))
        omission = self._as_float_or_none(behavior.get("omission"))
        false_action = self._as_float_or_none(behavior.get("false_action"))
        rt_stability = self._as_float_or_none(behavior.get("rt_stability"))
        if None in (acc, omission, false_action, rt_stability):
            s_b = 0.5
            fi_source = f"{fi_source}_neutral_behavior_default"
        else:
            s_b = 0.35 * max(0.0, min(1.0, acc)) + 0.20 * (1.0 - max(0.0, min(1.0, omission))) + 0.15 * (1.0 - max(0.0, min(1.0, false_action))) + 0.30 * max(0.0, min(1.0, rt_stability))

        fi = self._clip(100.0 * (0.55 * s_eeg + 0.15 * s_imu + 0.30 * s_b))
        return {"fi": fi, "fi_source": fi_source, "fi_unavailable_reason": "" if placeholder_zero_detected else "fi_missing_or_placeholder", "fi_valid": True, "fi_provisional": True, "fi_placeholder_zero_detected": placeholder_zero_detected, "fi_placeholder_zero_source": placeholder_zero_source}

    def _derive_fi_from_runtime(
        self,
        runtime: dict[str, Any],
        behavior_sample: dict[str, Any] | None = None,
        calibration_profile: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._resolve_runtime_fi(
            runtime,
            behavior_sample=behavior_sample,
            calibration_profile=calibration_profile,
        )

    def _derive_sqi_from_runtime(self, runtime: dict[str, Any]) -> tuple[float | None, str, str]:
        for key in ("sqi", "signal_quality_index", "quality_score"):
            val = self._as_float_or_none(runtime.get(key))
            if val is not None and val > 0.0:
                return max(0.0, min(1.0, val if val <= 1.0 else val / 100.0)), key, ""

        if runtime.get("error_flags"):
            return 0.0, "runtime_error_flags", "error_flags_present"

        attention_seen = runtime.get("attention") is not None or runtime.get("last_runtime_attention") is not None
        attention_fresh = bool(runtime.get("attention_fresh", runtime.get("last_runtime_attention_fresh", attention_seen)))
        gyro_fresh = bool(runtime.get("gyro_fresh", runtime.get("last_runtime_gyro_fresh", True)))
        stream_alive = bool(runtime.get("stream_alive", True))
        if attention_seen and stream_alive:
            score = 1.0
            if not attention_fresh:
                score -= 0.35
            if not gyro_fresh:
                score -= 0.25
            if runtime.get("warning_flags"):
                score -= 0.15
            return max(0.0, min(1.0, score)), "derived_freshness", ""

        return None, "unavailable", "no_attention_or_stream"

    def _normalize_training_runtime_sample(self, runtime: dict[str, Any]) -> dict[str, Any]:
        warning_flags = list(runtime.get("warning_flags") or [])
        error_flags = list(runtime.get("error_flags") or [])
        sqi_value, sqi_source, sqi_reason = self._derive_sqi_from_runtime(runtime)
        quality_state = runtime.get("quality_state")
        if quality_state is None:
            if error_flags:
                quality_state = "error"
            elif warning_flags:
                quality_state = "warning"
            elif sqi_value is not None and sqi_value >= 0.5:
                quality_state = "ok"
            else:
                quality_state = "unknown"
        enriched_runtime = dict(runtime)
        enriched_runtime.setdefault("sqi", sqi_value)
        enriched_runtime.setdefault("quality_state", quality_state)
        fi_resolved = self._resolve_runtime_fi(enriched_runtime, behavior_sample=(self._training_samples[-1] if self._training_samples else None), calibration_profile=self._current_calibration_profile())
        fi_value, fi_source, fi_reason = fi_resolved["fi"], fi_resolved["fi_source"], fi_resolved["fi_unavailable_reason"]
        raw_control_state = runtime.get("control_state") or "UNKNOWN"
        control_state = self._derive_control_state_from_fi(fi_value) if fi_value is not None else raw_control_state
        return {
            "now_ms": int(time.time() * 1000),
            "fi": fi_value,
            "sqi": sqi_value,
            "fi_source": fi_source,
            "sqi_source": sqi_source,
            "fi_unavailable_reason": fi_reason,
            "fi_valid": bool(fi_resolved.get("fi_valid") and fi_value is not None),
            "fi_provisional": bool(fi_resolved.get("fi_provisional")),
            "sqi_unavailable_reason": sqi_reason,
            "sqi_valid": sqi_value is not None,
            "raw_control_state": raw_control_state,
            "raw_fi": runtime.get("fi"),
            "raw_fi_raw": runtime.get("fi_raw"),
            "raw_fi_smoothed": runtime.get("fi_smoothed"),
            "raw_focus_index": runtime.get("focus_index"),
            "fi_placeholder_zero_detected": bool(fi_resolved.get("fi_placeholder_zero_detected")),
            "fi_placeholder_zero_source": fi_resolved.get("fi_placeholder_zero_source", ""),
            "attention": runtime.get("attention", runtime.get("last_runtime_attention")),
            "attention_age_ms": runtime.get("attention_age_ms"),
            "attention_fresh": bool(runtime.get("attention_fresh", runtime.get("last_runtime_attention_fresh", runtime.get("attention") is not None))),
            "gyro_fresh": bool(runtime.get("gyro_fresh", runtime.get("last_runtime_gyro_fresh", True))),
            "stream_alive": bool(runtime.get("stream_alive", True)),
            "control_state": control_state,
            "quality_state": quality_state,
            "warning_flags": warning_flags,
            "error_flags": error_flags,
        }

    def _record_training_event(self, evt_dict: dict[str, Any]) -> None:
        if self.interaction_enabled and self.session_type == "training":
            self._training_events.append(dict(evt_dict))

    def _stamp_game_view_dict(self, view_dict: dict[str, Any], *, tick_started_ms: int | None = None, tick_built_ms: int | None = None, tick_elapsed_ms: int | None = None) -> dict[str, Any]:
        """Attach timing diagnostics to the existing GameView dict.

        This does not create a new game pipeline.  It only marks when the
        existing backend view was built so QML can report whether it is
        displaying a stale frame.
        """
        out = dict(view_dict or {})
        hints = dict(out.get("layout_hints") or {})
        built_ms = int(tick_built_ms or int(time.time() * 1000))
        hints.update(
            {
                "backend_view_built_wall_ms": built_ms,
                "backend_tick_started_wall_ms": int(tick_started_ms or built_ms),
                "backend_tick_elapsed_ms": int(tick_elapsed_ms or 0),
                "backend_game_update_count": int(self.game_update_count),
                "backend_poll_interval_ms": int(self.poll_interval_sec * 1000),
                "backend_last_tick_seq": int(self._last_tick_seq),
            }
        )
        out["layout_hints"] = hints
        return out

    def _tick_loop(self) -> None:
        while not self._stop.is_set():
            tick_started_ms = int(time.time() * 1000)
            runtime = self._live_source.get_runtime_snapshot()
            with self._lock:
                self._last_tick_seq += 1
                self._last_tick_started_wall_ms = tick_started_ms
                self._client.update(runtime, int(self.poll_interval_sec * 1000))
                self._drain_game_events()
                view = self._client.build_game_view()
                tick_built_ms = int(time.time() * 1000)
                tick_elapsed_ms = max(0, tick_built_ms - tick_started_ms)
                self._last_tick_built_wall_ms = tick_built_ms
                self._last_tick_elapsed_ms = tick_elapsed_ms
                self.game_update_count += 1
                self.last_runtime_attention = runtime.get("attention")
                self.last_runtime_attention_fresh = bool(runtime.get("attention_fresh"))
                self.last_runtime_gyro_fresh = bool(runtime.get("gyro_fresh"))
                self.last_game_view = self._stamp_game_view_dict(
                    asdict(view),
                    tick_started_ms=tick_started_ms,
                    tick_built_ms=tick_built_ms,
                    tick_elapsed_ms=tick_elapsed_ms,
                )
                if self.interaction_enabled and self.session_type == "training":
                    self._training_runtime.append(self._normalize_training_runtime_sample(runtime))
                    now_ms = int(time.time() * 1000)
                    if now_ms - int(self._last_behavior_snapshot_ms) >= int(self._behavior_snapshot_interval_ms):
                        self._training_samples.append(self._snapshot_behavior_sample("periodic"))
                        self._last_behavior_snapshot_ms = now_ms
                    self._process_new_training_windows()
            time.sleep(self.poll_interval_sec)

    def _set_public_last_game_event(self, evt_dict: dict[str, Any]) -> None:
        """Expose only the event that should drive GUI feedback/platform state.

        TASK26 adds non-reportable semantic events such as target_spawn,
        score_update, and target_omitted for replay/report completeness.  Those
        events must be written to the training log, but they must not replace
        the immediate GUI feedback event produced by a pointer click.
        """
        self.last_game_event = evt_dict
        ep = evt_dict.get("payload") or {}
        self.last_game_action_name = str(ep.get("action_name") or "")
        ti = ep.get("target_index")
        self.last_game_target_index = ti if isinstance(ti, int) else None

    def _drain_game_events(self) -> None:
        events = self._client.collect_game_events()
        for evt in events:
            evt_dict = evt.to_dict()
            self._record_training_event(evt_dict)
            self.game_event_count += 1
            if not evt.reportable:
                continue
            self._set_public_last_game_event(evt_dict)
            self._platform_adapter.process_game_event(evt_dict, allow_mock=True)


    def _reset_training_buffers(self) -> None:
        self._training_samples = []
        self._training_runtime = []
        self._training_events = []
        self._training_windows = []
        self._difficulty_decisions = []
        self._session_start_game_event_count = self.game_event_count

    def _start_game_client(self, session_id: str, user_id: str, duration_ms: int) -> None:
        manifest = getattr(self._client, "manifest", {}) or {}
        default_difficulty = self._debug_difficulty_level if self._debug_difficulty_level is not None else manifest.get("default_difficulty", 1)
        self._client.start({
            "session_id": session_id,
            "user_id": user_id,
            "game_id": self.game_id,
            "difficulty": default_difficulty,
            "game_duration_ms": duration_ms,
        })
        print(
            f"[GAME START] game_id={self.game_id} session_id={session_id} difficulty_mode={self._difficulty_mode} debug_difficulty={self._debug_difficulty_level if self._debug_difficulty_level is not None else 'auto'} duration_ms={duration_ms}",
            flush=True,
        )

    def _current_game_hud(self) -> dict[str, Any]:
        view = self.last_game_view or {}
        return dict(view.get("hud") or {})

    def start_training_session(
        self,
        user_id: str | None = None,
        db_path: str = "data/relic_local.db",
        difficulty_mode: str | None = None,
        difficulty_level: Any | None = None,
        game_duration_ms: Any | None = None,
    ) -> dict[str, Any]:
        if self.interaction_enabled:
            return {"command": "start_training_session", "accepted": False, "status": "conflict", "message": "active_session_exists", "result": "conflict", "source": "live_control"}
        uid = str(user_id or self.user_id)
        self.user_id = uid
        now = datetime.now(timezone.utc)
        sid = f"training_{uid}_{now.strftime('%Y%m%d_%H%M%S')}"
        self.training_session_id = sid
        self.session_type = "training"
        self.last_training_status = "training_started"
        self.last_session_id = sid
        self._store = SqliteStore(db_path); self._store.connect()
        profile = self._store.get_user_profile(uid)
        calib = self._store.get_latest_calibration_profile(uid)

        # TASK24C-3: synchronize difficulty from the explicit session.start payload.
        # This is the hard guarantee: even if the operator only selects manual/auto
        # in the GUI and immediately starts training, the game client receives it.
        requested_mode = str(difficulty_mode or "").strip().lower()
        requested_level_text = str(difficulty_level if difficulty_level is not None else "").strip().lower()
        if requested_mode == "manual":
            try:
                self.set_debug_difficulty(max(1, min(5, int(difficulty_level))))
            except (TypeError, ValueError):
                self.set_debug_difficulty(None)
        elif requested_mode == "auto":
            # Desktop-card start buttons can carry a stale auto template even after
            # the operator applied a manual difficulty before starting.  Treat
            # auto/auto as "no explicit override" when a manual debug difficulty
            # is already staged, so pre-start Apply Difficulty is not cancelled.
            # A deliberate Apply Auto action sets _debug_difficulty_level to None
            # before session.start and therefore still starts in dynamic mode.
            if self._debug_difficulty_level is None or requested_level_text not in {"", "auto", "dynamic", "none", "null", "nan"}:
                self.set_debug_difficulty(None)

        duration_ms = self._training_duration_ms
        if game_duration_ms not in (None, "", "auto"):
            try:
                duration_ms = max(5000, int(game_duration_ms))
            except (TypeError, ValueError):
                duration_ms = self._training_duration_ms

        calib_dict = dict(calib or {})
        profile_dict = dict(profile or {})
        self._training_context = {
            "session_id": sid,
            "session_type": "training",
            "user_id": uid,
            "game_id": self.game_id,
            "started_at_ms": int(time.time()*1000),
            "db_path": db_path,
            "profile_status": "ok" if profile else "missing",
            "calibration_status": "ok" if calib else "missing",
            "calibration_fallback": calib is None,
            "calibration_id": calib_dict.get("calibration_id") or calib_dict.get("id") or profile_dict.get("last_calibration_id") or "",
            "calibration_profile": {
                "calibration_id": calib_dict.get("calibration_id") or calib_dict.get("id") or "",
                "attention_baseline": calib_dict.get("attention_baseline"),
                "attention_std": calib_dict.get("attention_std"),
                "signal_quality_baseline": calib_dict.get("signal_quality_baseline"),
                "gyro_noise_rms": calib_dict.get("gyro_noise_rms"),
                "valid": calib_dict.get("valid"),
                "failure_reason": calib_dict.get("failure_reason"),
            },
            "attention_low_threshold": profile_dict.get("attention_low_threshold"),
            "attention_high_threshold": profile_dict.get("attention_high_threshold"),
            "runtime_mode": "live-control",
            "report_path": "",
        }
        self._reset_training_buffers()
        manifest = getattr(self._client, "manifest", {}) or {}
        default_difficulty = self._debug_difficulty_level if self._debug_difficulty_level is not None else manifest.get("default_difficulty", 1)
        self._training_context.update({
            "difficulty_mode": self._difficulty_mode,
            "debug_difficulty": self._debug_difficulty_level if self._debug_difficulty_level is not None else "auto",
            "selected_difficulty_level": default_difficulty,
            "game_duration_ms": duration_ms,
            "dynamic_difficulty_enabled": self._debug_difficulty_level is None,
            "dda_enabled": True,
            "dda_mode": ("manual" if self._difficulty_mode == "manual" else "auto"),
        })
        self._dda_state = {"enabled": True, "last_decision_ms": 0, "cooldown_ms": 10000, "min_level": 1, "max_level": 5, "current_level": int(default_difficulty), "pending_up_count": 0, "pending_down_count": 0, "decision_events": [], "cooldown_block_count": 0, "conflict_hold_count": 0, "low_sqi_block_count": 0}
        if hasattr(self._client, "set_external_training_control_enabled"):
            self._client.set_external_training_control_enabled(True)
        self._start_game_client(sid, uid, duration_ms)
        self.interaction_enabled = True
        return {"command":"start_training_session","accepted":True,"status":"training_started","result":"training_started","session_id":sid,"session_context":dict(self._training_context),"source":"live_control"}

    def _summarize_field(self, field_name: str, rows: list[dict[str, Any]]) -> str:
        counts: dict[str, int] = {}
        for row in rows:
            val = row.get(field_name)
            if val in (None, ""):
                continue
            key = str(val)
            counts[key] = counts.get(key, 0) + 1
        if not counts:
            return "unknown"
        return ",".join(f"{k}:{v}" for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

    def _snapshot_behavior_sample(self, reason: str = "periodic_or_input") -> dict[str, Any]:
        sample = self._client.collect_behavior_sample().to_dict()
        sample["now_ms"] = int(time.time() * 1000)
        sample["sample_index"] = len(self._training_samples)
        sample["behavior_source"] = reason
        return sample

    def _build_training_windows(self, runtime_rows: list[dict[str, Any]], behavior_rows: list[dict[str, Any]] | None = None, final_behavior_sample: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if not runtime_rows:
            return []
        step_ms = max(1, int(self.poll_interval_sec * 1000))
        size = max(1, int(self._training_window_ms / step_ms))
        windows: list[dict[str, Any]] = []
        for idx, start in enumerate(range(0, len(runtime_rows), size)):
            rows = runtime_rows[start:start + size]
            fi_valid = [float(r["fi"]) for r in rows if r.get("fi_valid") and r.get("fi") is not None]
            sqi_valid = [float(r["sqi"]) for r in rows if r.get("sqi_valid") and r.get("sqi") is not None]
            fi_sources = self._summarize_field("fi_source", rows)
            control_summary = self._summarize_field("control_state", rows)
            quality_summary = self._summarize_field("quality_state", rows)
            quality_counts: dict[str, int] = {}
            for r in rows:
                q = str(r.get("quality_state") or "unknown").lower()
                quality_counts[q] = quality_counts.get(q, 0) + 1
            low_sqi_count = sum(1 for r in rows if r.get("sqi") is not None and float(r["sqi"]) < 0.5)
            sqi_valid_ratio = (len(sqi_valid) / len(rows)) if rows else 0.0
            sqi_avg = (sum(sqi_valid) / len(sqi_valid)) if sqi_valid else None
            blocked = (sqi_avg is None or sqi_avg < 0.50 or sqi_valid_ratio < 0.60 or (quality_counts.get("error", 0) + quality_counts.get("unreliable", 0)) > (len(rows) / 2.0))
            signal_gate_status = "blocked" if blocked else "open"
            window_start_ms = int(rows[0].get("now_ms", 0))
            window_end_ms = int(rows[-1].get("now_ms", 0))
            behavior_rows = behavior_rows or []
            grace_ms = 500
            in_window = [b for b in behavior_rows if isinstance(b, dict) and b.get("now_ms") is not None and window_start_ms <= int(b.get("now_ms")) <= (window_end_ms + grace_ms)]
            prev_rows = [b for b in behavior_rows if isinstance(b, dict) and b.get("now_ms") is not None and int(b.get("now_ms")) < window_start_ms]
            chosen_behavior: dict[str, Any] | None = None
            behavior_source = "unavailable"
            if in_window:
                chosen_behavior = in_window[-1]
                behavior_source = "window_snapshot"
            elif prev_rows:
                chosen_behavior = prev_rows[-1]
                behavior_source = "carried_forward"
            elif final_behavior_sample:
                chosen_behavior = dict(final_behavior_sample)
                behavior_source = "session_final_summary"
            behavior_ok = chosen_behavior is not None and all(chosen_behavior.get(k) is not None for k in ("accuracy", "omission", "false_action", "rt_stability"))
            accuracy = float(chosen_behavior["accuracy"]) if behavior_ok else None
            omission = float(chosen_behavior["omission"]) if behavior_ok else None
            false_action = float(chosen_behavior["false_action"]) if behavior_ok else None
            rt_stability = float(chosen_behavior["rt_stability"]) if behavior_ok else None
            rt_stability_source = "snapshot_last" if rt_stability is not None else "unavailable"
            delta_target = delta_correct = delta_omission = delta_false = None
            if len(in_window) >= 2:
                first = in_window[0]
                last = in_window[-1]
                try:
                    delta_target = max(0, int(last.get("target_count", 0)) - int(first.get("target_count", 0)))
                    delta_correct = max(0, int(last.get("correct_count", 0)) - int(first.get("correct_count", 0)))
                    delta_omission = max(0, int(last.get("omission_count", 0)) - int(first.get("omission_count", 0)))
                    delta_false = max(0, int(last.get("false_action_count", 0)) - int(first.get("false_action_count", 0)))
                    accuracy = delta_correct / max(delta_target, 1)
                    omission = delta_omission / max(delta_target, 1)
                    false_action = delta_false / max(delta_correct + delta_false, 1)
                except (TypeError, ValueError):
                    behavior_source = "window_snapshot_cumulative_fallback"
            perf = (0.40 * accuracy + 0.25 * rt_stability + 0.20 * (1.0 - omission) + 0.15 * (1.0 - false_action)) if behavior_ok else None
            fi_avg = (sum(fi_valid) / len(fi_valid)) if fi_valid else None
            stable_count = sum(1 for r in rows if r.get("control_state") == "STABLE_FOCUS")
            high_count = sum(1 for r in rows if r.get("control_state") == "HIGH_FOCUS")
            distracted_count = sum(1 for r in rows if r.get("control_state") == "DISTRACTED")
            fatigued_count = sum(1 for r in rows if r.get("control_state") == "FATIGUED")
            stable_ms = (stable_count + high_count) * step_ms
            if not behavior_ok:
                action, reason = "insufficient_samples", "insufficient_behavior_samples"
            elif blocked:
                action, reason = "blocked_by_low_sqi", "signal_quality_gate_blocked"
            elif fi_avg is not None and perf is not None and ((fi_avg >= 65 and perf < 0.60) or (fi_avg < 45 and perf >= 0.72)):
                action, reason = "conflict_hold", "fi_perf_conflict"
            elif fi_avg is not None and perf is not None and sqi_avg is not None and sqi_avg >= 0.70 and fi_avg >= 65 and (stable_count + high_count) > (len(rows) / 2.0) and perf >= 0.72:
                action, reason = "suggest_level_up", "high_fi_high_perf"
            elif fi_avg is not None and perf is not None and sqi_avg is not None and sqi_avg >= 0.50 and ((fi_avg < 40 and perf < 0.60) or perf < 0.45 or (omission is not None and omission > 0.45) or (false_action is not None and false_action > 0.35) or (rt_stability is not None and rt_stability < 0.45)):
                action, reason = "suggest_level_down", "low_fi_or_poor_perf"
            else:
                action, reason = "hold", "within_stable_band"
            if signal_gate_status == "blocked":
                feedback = "signal_check"
            elif fi_avg is not None and perf is not None and fi_avg >= 65 and perf >= 0.72:
                feedback = "reward"
            elif fi_avg is not None and perf is not None and ((fi_avg < 40 and perf < 0.55) or fatigued_count > len(rows) / 2.0):
                feedback = "protect"
            elif fi_avg is not None and perf is not None and (fi_avg < 55 or perf < 0.60):
                feedback = "assist"
            else:
                feedback = "maintain"
            windows.append({
                "window_index": idx, "window_start_ms": window_start_ms, "window_end_ms": window_end_ms,
                "duration_ms": max(0, window_end_ms - window_start_ms), "sample_count": len(rows),
                "fi_avg": fi_avg, "fi_min": min(fi_valid) if fi_valid else None, "fi_max": max(fi_valid) if fi_valid else None, "fi_last": fi_valid[-1] if fi_valid else None,
                "fi_trend": ((fi_valid[-1] - fi_valid[0]) if len(fi_valid) >= 2 else 0.0) if fi_valid else None, "fi_valid_ratio": (len(fi_valid) / len(rows)) if rows else 0.0,
                "fi_provisional_ratio": (sum(1 for r in rows if r.get("fi_valid") and r.get("fi_provisional")) / len(fi_valid)) if fi_valid else 0.0,
                "fi_source_summary": fi_sources, "control_state_summary": control_summary, "stable_focus_sample_count": stable_count, "high_focus_sample_count": high_count,
                "distracted_sample_count": distracted_count, "fatigued_sample_count": fatigued_count, "sqi_avg": sqi_avg, "sqi_min": min(sqi_valid) if sqi_valid else None,
                "sqi_valid_ratio": sqi_valid_ratio, "low_sqi_sample_count": low_sqi_count, "quality_state_summary": quality_summary, "signal_gate_status": signal_gate_status,
                "accuracy_window": accuracy, "omission_window": omission, "false_action_window": false_action, "rt_stability_window": rt_stability,
                "target_count_window": chosen_behavior.get("target_count") if chosen_behavior else None, "correct_count_window": chosen_behavior.get("correct_count") if chosen_behavior else None,
                "omission_count_window": chosen_behavior.get("omission_count") if chosen_behavior else None, "false_action_count_window": chosen_behavior.get("false_action_count") if chosen_behavior else None,
                "perf_window": perf, "stable_focus_duration_ms": stable_ms, "recommended_difficulty_action": action, "recommended_feedback_mode": feedback,
                "decision_reason": reason, "decision_confidence": (0.9 if action in {"suggest_level_up", "suggest_level_down", "blocked_by_low_sqi"} else 0.7),
                "behavior_window_source": behavior_source,
                "behavior_window_sample_count": len(in_window),
                "behavior_window_first_index": in_window[0].get("sample_index") if in_window else None,
                "behavior_window_last_index": in_window[-1].get("sample_index") if in_window else None,
                "behavior_window_delta_target_count": delta_target,
                "behavior_window_delta_correct_count": delta_correct,
                "behavior_window_delta_omission_count": delta_omission,
                "behavior_window_delta_false_action_count": delta_false,
                "rt_stability_source": rt_stability_source,
                "neural_state_evidence": {"fi_avg": fi_avg, "fi_source_summary": fi_sources, "control_state_summary": control_summary},
                "signal_quality_evidence": {"sqi_avg": sqi_avg, "sqi_valid_ratio": sqi_valid_ratio, "signal_gate_status": signal_gate_status},
                "behavior_evidence": {"perf_window": perf, "accuracy_window": accuracy, "omission_window": omission, "false_action_window": false_action, "rt_stability_window": rt_stability},
                "adaptation_evidence": {"recommended_difficulty_action": action, "recommended_feedback_mode": feedback, "decision_reason": reason},
            })
        return windows


    def _process_window_decision(self, window: dict[str, Any], allow_apply: bool = True) -> dict[str, Any]:
        now_ms = int(window.get("window_end_ms") or int(time.time()*1000))
        st = self._dda_state or {}
        mode = "manual" if self._difficulty_mode == "manual" else "auto"
        requested = str(window.get("recommended_difficulty_action") or "hold")
        current_level = int(st.get("current_level") or 1)
        cooldown = int(st.get("cooldown_ms") or 10000)
        last_ms = int(st.get("last_decision_ms") or 0)
        cooldown_remaining = 0 if last_ms <= 0 else max(0, cooldown - max(0, now_ms - last_ms))
        applied_action = "hold"
        applied = False
        reason = "hold"
        if mode == "manual":
            reason = "manual_mode_no_apply"
        elif requested in {"blocked_by_low_sqi", "conflict_hold", "insufficient_samples"} or window.get("signal_gate_status") == "blocked":
            applied_action = "blocked"
            reason = "signal_quality_gate_blocked" if window.get("signal_gate_status") == "blocked" else requested
            st["low_sqi_block_count"] = int(st.get("low_sqi_block_count", 0)) + (1 if window.get("signal_gate_status") == "blocked" else 0)
            st["conflict_hold_count"] = int(st.get("conflict_hold_count", 0)) + (1 if requested == "conflict_hold" else 0)
        else:
            if requested == "suggest_level_up":
                st["pending_up_count"] = int(st.get("pending_up_count", 0)) + 1
                st["pending_down_count"] = 0
            elif requested == "suggest_level_down":
                st["pending_down_count"] = int(st.get("pending_down_count", 0)) + 1
                st["pending_up_count"] = 0
            else:
                st["pending_up_count"] = 0; st["pending_down_count"] = 0
            if cooldown_remaining > 0:
                applied_action = "blocked"; reason = "cooldown_active"; st["cooldown_block_count"] = int(st.get("cooldown_block_count", 0)) + 1
            elif requested == "suggest_level_up" and int(st.get("pending_up_count", 0)) >= 2 and current_level < int(st.get("max_level", 5)) and allow_apply:
                res = self._client.apply_training_control({"action": "level_up", "reason": "consecutive_level_up", "window_index": window.get("window_index"), "fi_window_avg": window.get("fi_avg"), "sqi_window_avg": window.get("sqi_avg"), "perf_window": window.get("perf_window")}) if hasattr(self._client, "apply_training_control") else {"applied": False, "from_level": current_level, "to_level": current_level, "reason": "client_missing"}
                applied = bool(res.get("applied")); applied_action = "level_up" if applied else "hold"; reason = str(res.get("reason")); st["current_level"] = int(res.get("to_level", current_level)); st["last_decision_ms"] = now_ms if applied else last_ms
                if applied:
                    self._drain_game_events()
                    self.last_game_view = asdict(self._client.build_game_view())
            elif requested == "suggest_level_down" and int(st.get("pending_down_count", 0)) >= 2 and current_level > int(st.get("min_level", 1)) and allow_apply:
                res = self._client.apply_training_control({"action": "level_down", "reason": "consecutive_level_down", "window_index": window.get("window_index"), "fi_window_avg": window.get("fi_avg"), "sqi_window_avg": window.get("sqi_avg"), "perf_window": window.get("perf_window")}) if hasattr(self._client, "apply_training_control") else {"applied": False, "from_level": current_level, "to_level": current_level, "reason": "client_missing"}
                applied = bool(res.get("applied")); applied_action = "level_down" if applied else "hold"; reason = str(res.get("reason")); st["current_level"] = int(res.get("to_level", current_level)); st["last_decision_ms"] = now_ms if applied else last_ms
                if applied:
                    self._drain_game_events()
                    self.last_game_view = asdict(self._client.build_game_view())
            else:
                if requested in {"suggest_level_up", "suggest_level_down"} and ((requested == "suggest_level_up" and int(st.get("pending_up_count", 0)) < 2) or (requested == "suggest_level_down" and int(st.get("pending_down_count", 0)) < 2)):
                    reason = "waiting_for_consecutive_windows"
                elif (requested == "suggest_level_up" and current_level >= int(st.get("max_level", 5))) or (requested == "suggest_level_down" and current_level <= int(st.get("min_level", 1))):
                    reason = "level_limit_reached"
                else:
                    reason = "hold"
        decision = {"window_index": window.get("window_index"), "decision_time_ms": now_ms, "mode": mode, "current_level": current_level, "requested_action": requested, "applied_action": applied_action, "from_level": current_level, "to_level": int(st.get("current_level", current_level)), "applied": applied, "reason": reason, "cooldown_remaining_ms": cooldown_remaining, "consecutive_up_count": int(st.get("pending_up_count", 0)), "consecutive_down_count": int(st.get("pending_down_count", 0)), "fi_window_avg": window.get("fi_avg"), "sqi_window_avg": window.get("sqi_avg"), "perf_window": window.get("perf_window"), "accuracy_window": window.get("accuracy_window"), "omission_window": window.get("omission_window"), "false_action_window": window.get("false_action_window"), "rt_stability_window": window.get("rt_stability_window"), "signal_gate_status": window.get("signal_gate_status"), "behavior_window_source": window.get("behavior_window_source"), "decision_confidence": window.get("decision_confidence")}
        self._difficulty_decisions.append(decision)
        self._dda_state = st
        return decision

    def _process_new_training_windows(self, final_behavior_sample: dict[str, Any] | None = None, flush_incomplete: bool = False) -> None:
        """Build/process only completed online windows.

        _build_training_windows(...) always includes the current trailing partial
        chunk.  Online DDA must not append that partial chunk every tick; doing
        so creates duration_ms=0/sample_count=1 windows and shifts the processed
        window index ahead of real five-second windows.
        """
        windows = self._build_training_windows(
            self._training_runtime,
            self._training_samples,
            final_behavior_sample,
        )
        existing = len(self._training_windows)
        step_ms = max(1, int(self.poll_interval_sec * 1000))
        full_samples = max(1, int(self._training_window_ms / step_ms))
        min_flush_samples = max(1, int(full_samples * 0.6))

        for w in windows[existing:]:
            sample_count = int(w.get("sample_count", 0) or 0)
            is_full = sample_count >= full_samples
            is_flush_partial = bool(flush_incomplete and sample_count >= min_flush_samples)

            if not is_full and not flush_incomplete:
                break

            self._training_windows.append(w)

            if is_full:
                self._process_window_decision(w, allow_apply=True)
            elif is_flush_partial:
                self._process_window_decision(w, allow_apply=False)


    def end_training_session(self) -> dict[str, Any]:
        if not self.interaction_enabled or not self.training_session_id or self.session_type != "training":
            return {"command":"end_training_session","accepted":True,"status":"training_stopped","result":"noop","message":"no_active_training_session","source":"live_control"}
        self.interaction_enabled = False
        self._client.stop("training_completed")
        for evt in self._client.collect_game_events():
            evt_dict = evt.to_dict()
            self._record_training_event(evt_dict)
            self.last_game_event = evt_dict
            self.game_event_count += 1
        sample = self._client.collect_behavior_sample().to_dict()
        view = self._client.build_game_view()
        now_ms = int(time.time()*1000)
        started = int(self._training_context.get("started_at_ms") or now_ms)
        total_duration_ms = max(0, now_ms - started)
        duration_sec = round(total_duration_ms / 1000.0, 3)
        fi_valid_rows=[x for x in self._training_runtime if x.get("fi_valid") and x.get("fi") is not None]
        sqi_valid_rows=[x for x in self._training_runtime if x.get("sqi_valid") and x.get("sqi") is not None]
        fi_vals=[float(x.get("fi")) for x in fi_valid_rows]
        sqi_vals=[float(x.get("sqi")) for x in sqi_valid_rows]
        runtime_step_ms = int(self.poll_interval_sec * 1000)
        valid_rows = [x for x in self._training_runtime if not x.get("error_flags") and str(x.get("quality_state", "")).lower() != "error"]
        warning_rows = [x for x in self._training_runtime if x.get("warning_flags") or str(x.get("quality_state", "")).lower() == "warning"]
        error_rows = [x for x in self._training_runtime if x.get("error_flags") or str(x.get("quality_state", "")).lower() == "error"]
        valid_duration_ms = len(valid_rows) * runtime_step_ms
        warning_duration_ms = len(warning_rows) * runtime_step_ms
        error_duration_ms = len(error_rows) * runtime_step_ms
        session_game_event_count = max(0, self.game_event_count - self._session_start_game_event_count)
        behavior_sample_count = max(len(self._training_samples), 1 if sample else 0)
        log_path = f"logs/sessions/{self.training_session_id}.jsonl"
        self._process_new_training_windows(final_behavior_sample=sample, flush_incomplete=True)
        training_windows = list(self._training_windows)
        self._write_training_log(log_path, sample, view, total_duration_ms, training_windows)
        score_update_count = sum(1 for evt in self._training_events if ((evt.get("payload") or {}).get("event_type") == "score_update" or evt.get("event_type") == "score_update") )
        target_spawn_count = sum(1 for evt in self._training_events if ((evt.get("payload") or {}).get("event_type") == "target_spawn" or evt.get("event_type") == "target_spawn") )
        target_click_count = sum(1 for evt in self._training_events if ((evt.get("payload") or {}).get("event_type") == "target_click" or evt.get("event_type") == "target_click") )
        background_click_count = sum(1 for evt in self._training_events if ((evt.get("payload") or {}).get("event_type") == "background_click" or evt.get("event_type") == "background_click") )
        target_omitted_count = sum(1 for evt in self._training_events if ((evt.get("payload") or {}).get("event_type") == "target_omitted" or evt.get("event_type") == "target_omitted") )
        level_changed_count = sum(1 for evt in self._training_events if ((evt.get("payload") or {}).get("event_type") == "level_changed" or evt.get("event_type") == "level_changed") )
        summary={
            "session_id":self.training_session_id,
            "user_id":self.user_id,
            "game_id":self.game_id,
            "started_at":datetime.fromtimestamp(started/1000,tz=timezone.utc).isoformat(),
            "ended_at":datetime.now(timezone.utc).isoformat(),
            "status":"training_completed",
            "session_type":"training",
            "score":view.score,
            "combo":view.combo,
            "max_combo":view.hud.get("max_combo"),
            "level_final":view.level,
            "difficulty_mode": self._difficulty_mode,
            "debug_difficulty": self._debug_difficulty_level if self._debug_difficulty_level is not None else "auto",
            "selected_difficulty_level": self._debug_difficulty_level if self._debug_difficulty_level is not None else view.level,
            "effective_level": view.hud.get("effective_level", view.level),
            "dynamic_difficulty_enabled": view.hud.get("dynamic_difficulty_enabled"),
            "game_duration_ms": view.hud.get("game_duration_ms"),
            "elapsed_ms": view.hud.get("elapsed_ms"),
            "time_left_ms": view.hud.get("time_left_ms"),
            "game_completed": view.hud.get("game_completed"),
            "movement_type": view.hud.get("movement_type"),
            "target_pressure_level": view.hud.get("target_pressure_level"),
            "target_count":sample.get("target_count"),
            "correct_count":sample.get("correct_count"),
            "omission_count":sample.get("omission_count"),
            "false_action_count":sample.get("false_action_count"),
            "accuracy":sample.get("accuracy"),
            "omission":sample.get("omission"),
            "false_action":sample.get("false_action"),
            "rt_stability":sample.get("rt_stability"),
            "behavior_sample_count": behavior_sample_count,
            "game_event_count": session_game_event_count,
            "log_path": log_path,
            "duration_sec": duration_sec,
            "total_duration_ms": total_duration_ms,
            "valid_duration_ms": valid_duration_ms,
            "warning_duration_ms": warning_duration_ms,
            "error_duration_ms": error_duration_ms,
            "fi_avg":(sum(fi_vals)/len(fi_vals) if fi_vals else None),
            "sqi_avg":(sum(sqi_vals)/len(sqi_vals) if sqi_vals else None),
            "final_fi_avg":(sum(fi_vals)/len(fi_vals) if fi_vals else None),
            "final_sqi_avg":(sum(sqi_vals)/len(sqi_vals) if sqi_vals else None),
            "fi_min": (min(fi_vals) if fi_vals else None),
            "fi_max": (max(fi_vals) if fi_vals else None),
            "fi_last": (fi_vals[-1] if fi_vals else None),
            "sqi_min": (min(sqi_vals) if sqi_vals else None),
            "sqi_max": (max(sqi_vals) if sqi_vals else None),
            "sqi_last": (sqi_vals[-1] if sqi_vals else None),
            "calibration_status":self._training_context.get("calibration_status","missing"),
            "calibration_id":self._training_context.get("calibration_id",""),
            "attention_baseline":(self._training_context.get("calibration_profile") or {}).get("attention_baseline"),
            "attention_std":(self._training_context.get("calibration_profile") or {}).get("attention_std"),
            "profile_status":self._training_context.get("profile_status","missing"),
            "fi_source_summary": self._summarize_field("fi_source", self._training_runtime),
            "sqi_source_summary": self._summarize_field("sqi_source", self._training_runtime),
            "control_state_summary": self._summarize_field("control_state", self._training_runtime),
            "raw_control_state_summary": self._summarize_field("raw_control_state", self._training_runtime),
            "fi_provisional_ratio": (sum(1 for x in fi_valid_rows if x.get("fi_provisional")) / len(fi_valid_rows) if fi_valid_rows else None),
            "score_update_count": score_update_count,
            "target_spawn_count": target_spawn_count,
            "target_click_count": target_click_count,
            "background_click_count": background_click_count,
            "target_omitted_count": target_omitted_count,
            "level_changed_count": level_changed_count,
            "quality_state_summary": self._summarize_field("quality_state", self._training_runtime),
            "warning_count":sum(len(x.get("warning_flags",[])) for x in self._training_runtime),
            "error_count":sum(len(x.get("error_flags",[])) for x in self._training_runtime),
            "training_window_count": len(training_windows),
            "fi_window_avg": (sum(w["fi_avg"] for w in training_windows if w.get("fi_avg") is not None) / len([w for w in training_windows if w.get("fi_avg") is not None]) if any(w.get("fi_avg") is not None for w in training_windows) else None),
            "fi_window_min": (min(w["fi_min"] for w in training_windows if w.get("fi_min") is not None) if any(w.get("fi_min") is not None for w in training_windows) else None),
            "fi_window_max": (max(w["fi_max"] for w in training_windows if w.get("fi_max") is not None) if any(w.get("fi_max") is not None for w in training_windows) else None),
            "perf_window_avg": (sum(w["perf_window"] for w in training_windows if w.get("perf_window") is not None) / len([w for w in training_windows if w.get("perf_window") is not None]) if any(w.get("perf_window") is not None for w in training_windows) else None),
            "sqi_window_avg": (sum(w["sqi_avg"] for w in training_windows if w.get("sqi_avg") is not None) / len([w for w in training_windows if w.get("sqi_avg") is not None]) if any(w.get("sqi_avg") is not None for w in training_windows) else None),
            "low_sqi_window_count": sum(1 for w in training_windows if w.get("signal_gate_status") == "blocked"),
            "stable_focus_window_count": sum(1 for w in training_windows if (w.get("stable_focus_sample_count", 0) + w.get("high_focus_sample_count", 0)) > (w.get("sample_count", 0) / 2.0)),
            "high_focus_window_count": sum(1 for w in training_windows if w.get("high_focus_sample_count", 0) > (w.get("sample_count", 0) / 2.0)),
            "stable_focus_total_ms": sum(int(w.get("stable_focus_duration_ms") or 0) for w in training_windows),
            "difficulty_suggestion_summary": self._summarize_field("recommended_difficulty_action", training_windows),
            "feedback_mode_summary": self._summarize_field("recommended_feedback_mode", training_windows),
            "conflict_hold_count": sum(1 for w in training_windows if w.get("recommended_difficulty_action") == "conflict_hold"),
            "signal_check_count": sum(1 for w in training_windows if w.get("recommended_feedback_mode") == "signal_check"),
            "behavior_window_source_summary": self._summarize_field("behavior_window_source", training_windows),
            "carried_forward_window_count": sum(1 for w in training_windows if w.get("behavior_window_source") == "carried_forward"),
            "session_final_behavior_window_count": sum(1 for w in training_windows if w.get("behavior_window_source") == "session_final_summary"),
            "window_snapshot_behavior_window_count": sum(1 for w in training_windows if str(w.get("behavior_window_source", "")).startswith("window_snapshot")),
            "insufficient_behavior_window_count": sum(1 for w in training_windows if w.get("recommended_difficulty_action") == "insufficient_samples"),
            "dda_enabled": True, "dda_mode": ("manual" if self._difficulty_mode == "manual" else "auto"),
            "difficulty_decision_count": len(self._difficulty_decisions),
            "difficulty_changed_count": sum(1 for d in self._difficulty_decisions if d.get("applied")),
            "dda_applied_count": sum(1 for d in self._difficulty_decisions if d.get("applied")),
            "dda_level_up_count": sum(1 for d in self._difficulty_decisions if d.get("applied_action") == "level_up"),
            "dda_level_down_count": sum(1 for d in self._difficulty_decisions if d.get("applied_action") == "level_down"),
            "dda_blocked_count": sum(1 for d in self._difficulty_decisions if d.get("applied_action") == "blocked"),
            "dda_hold_count": sum(1 for d in self._difficulty_decisions if d.get("applied_action") == "hold"),
            "dda_final_level": int((self._dda_state or {}).get("current_level", self._debug_difficulty_level if self._debug_difficulty_level is not None else view.level)),
            "dda_decision_summary": self._summarize_field("applied_action", self._difficulty_decisions),
            "dda_cooldown_block_count": int((self._dda_state or {}).get("cooldown_block_count", 0)),
            "dda_conflict_hold_count": int((self._dda_state or {}).get("conflict_hold_count", 0)),
            "dda_low_sqi_block_count": int((self._dda_state or {}).get("low_sqi_block_count", 0)),
        }
        report_path = write_session_report(summary, {"event_count": session_game_event_count, "behavior_sample_count": behavior_sample_count}, out_dir="reports/sessions")
        summary["report_path"]=report_path
        self._store.upsert_training_session(summary)
        self.last_game_view = asdict(view)
        self._training_context["report_path"]=report_path
        self.last_report_path = report_path
        self.last_training_status = "training_completed"
        self.last_session_id = str(self.training_session_id or "")
        self.session_type = ""
        return {"command":"end_training_session","accepted":True,"status":"training_completed","result":"training_completed","report_path":report_path,"session_id":self.training_session_id,"source":"live_control"}


    def _write_training_log(self, log_path: str, sample: dict[str, Any], view: Any, total_duration_ms: int, training_windows: list[dict[str, Any]] | None = None) -> None:
        path = Path(log_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        def rec(record_type: str, payload: dict[str, Any]) -> dict[str, Any]:
            # Keep both keys: older tools used "type", replay/report tooling uses "event_type".
            return {"type": record_type, "event_type": record_type, "payload": dict(payload or {})}

        records: list[dict[str, Any]] = [
            rec("session_context", dict(self._training_context)),
            rec("runtime_summary", {
                "sample_count": len(self._training_runtime),
                "event_count": len(self._training_events),
                "behavior_sample_count": len(self._training_samples),
                "total_duration_ms": total_duration_ms,
                "fi_source_summary": self._summarize_field("fi_source", self._training_runtime),
                "sqi_source_summary": self._summarize_field("sqi_source", self._training_runtime),
                "control_state_summary": self._summarize_field("control_state", self._training_runtime),
                "quality_state_summary": self._summarize_field("quality_state", self._training_runtime),
            }),
        ]
        for idx, runtime_sample in enumerate(self._training_runtime):
            payload = dict(runtime_sample)
            payload.setdefault("sample_index", idx)
            records.append(rec("runtime_sample", payload))
        for idx, window in enumerate(training_windows or []):
            payload = dict(window)
            payload.setdefault("window_index", idx)
            records.append(rec("training_window", payload))
        for idx, behavior_sample in enumerate(self._training_samples):
            payload = dict(behavior_sample)
            payload.setdefault("sample_index", idx)
            records.append(rec("behavior_sample_snapshot", payload))
        for idx, decision in enumerate(self._difficulty_decisions):
            payload = dict(decision)
            payload.setdefault("sample_index", idx)
            records.append(rec("difficulty_decision", payload))
        for idx, evt in enumerate(self._training_events):
            payload = dict(evt)
            payload.setdefault("sample_index", idx)
            records.append(rec("game_event", payload))
        records.extend([
            rec("behavior_sample", dict(sample or {})),
            rec("game_view_summary", {"score": getattr(view, "score", None), "combo": getattr(view, "combo", None), "level": getattr(view, "level", None), "hud": getattr(view, "hud", {})}),
        ])
        with path.open("w", encoding="utf-8") as fh:
            for record in records:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")


    def start_live_debug_session(self, user_id: str | None = None) -> dict[str, Any]:
        if self.interaction_enabled and self.session_type == "training":
            return {"command": "start_mock_session", "accepted": False, "status": "conflict", "message": "active_training_session", "result": "conflict", "source": "live_control"}
        uid = str(user_id or self.user_id)
        self.user_id = uid
        sid = f"live_debug_{uid}_{time.strftime('%Y%m%d_%H%M%S')}"
        # avoid same-second reuse
        if sid == self.live_debug_session_id:
            sid = f"{sid}_{int(time.time() * 1000) % 1000:03d}"
        self.live_debug_session_id = sid
        manifest = getattr(self._client, "manifest", {}) or {}
        default_difficulty = self._debug_difficulty_level if self._debug_difficulty_level is not None else manifest.get("default_difficulty", 1)
        self._training_context.update({
            "difficulty_mode": self._difficulty_mode,
            "debug_difficulty": self._debug_difficulty_level if self._debug_difficulty_level is not None else "auto",
            "selected_difficulty_level": default_difficulty,
            "game_duration_ms": self._live_debug_duration_ms,
        })
        self._start_game_client(sid, uid, self._live_debug_duration_ms)
        self.interaction_enabled = True
        self.session_type = "debug"
        self.last_session_id = sid
        return {"command": "start_mock_session", "accepted": True, "status": "live_debug_started", "message": "live debug session started", "result": "live_debug_started", "session_id": sid, "source": "live_control"}

    def end_live_debug_session(self) -> dict[str, Any]:
        if not self.interaction_enabled or not self.live_debug_session_id:
            return {"command": "end_session", "accepted": True, "status": "noop", "message": "no_active_session", "result": "noop", "source": "live_control"}
        self.interaction_enabled = False
        self.session_type = ""
        self._client.stop("live_debug_stopped")
        self._client.collect_game_events()
        return {"command": "end_session", "accepted": True, "status": "live_debug_stopped", "message": "live debug session stopped", "result": "live_debug_stopped", "source": "live_control"}

    def handle_pointer_click(self, payload: dict[str, Any]) -> dict[str, Any]:
        active_session_id = self.training_session_id if self.session_type == "training" else self.live_debug_session_id
        if not self.interaction_enabled or not active_session_id:
            return {"result": "no_active_live_debug_session", "status": "ignored", "reason": "no_active_live_debug_session", "source": "live_control"}
        with self._lock:
            self._event_seq += 1
            now_ms = int(time.time() * 1000)
            raw_created_at = payload.get("client_created_at_ms")
            try:
                created_at_ms = int(raw_created_at)
            except (TypeError, ValueError):
                created_at_ms = now_ms
            # Guard against stale/out-of-clock payloads while still preserving
            # the low-latency press timestamp from QML when available.
            if created_at_ms <= 0 or abs(now_ms - created_at_ms) > 5000:
                created_at_ms = now_ms
            ge = GameInputEvent(event_id=f"live_ctrl_input_{self._event_seq}", session_id=active_session_id, game_id=self.game_id, input_type="pointer_click", created_at_ms=created_at_ms, source="minimal_game_canvas", x_norm=float(payload.get("x_norm", 0.0)), y_norm=float(payload.get("y_norm", 0.0)), button=0, raw_event_type="pointer_click", debug_hit=payload.get("hit"), payload=dict(payload))
            input_diag = payload.get("diagnostic") if isinstance(payload.get("diagnostic"), dict) else {}
            print(f"[GAME INPUT] type={ge.input_type} x={ge.x_norm:.3f} y={ge.y_norm:.3f} session_id={ge.session_id}", flush=True)
            print(
                "[GAME INPUT DEBUG] "
                + json.dumps(
                    {
                        "now_ms": now_ms,
                        "client_created_at_ms": created_at_ms,
                        "delivery_latency_ms": max(0, now_ms - created_at_ms),
                        "x_norm": ge.x_norm,
                        "y_norm": ge.y_norm,
                        "display_frame_id": input_diag.get("frame_id", payload.get("display_frame_id")),
                        "display_target_id": input_diag.get("display_target_id", payload.get("display_target_id", "")),
                        "display_target_x": input_diag.get("display_target_x", payload.get("display_target_x")),
                        "display_target_y": input_diag.get("display_target_y", payload.get("display_target_y")),
                        "display_hit_radius": input_diag.get("display_hit_radius", payload.get("display_hit_radius")),
                        "display_dist": input_diag.get("display_dist", payload.get("display_dist")),
                        "display_hit_candidate": input_diag.get("display_hit_candidate", payload.get("display_hit_candidate")),
                        "display_target_age_ms": input_diag.get("display_target_age_ms", payload.get("display_target_age_ms")),
                        "display_progress": input_diag.get("display_progress", payload.get("display_progress")),
                        "ring_progress": input_diag.get("ring_progress", payload.get("ring_progress")),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                flush=True,
            )
            self._client.handle_input(ge)
            events = self._client.collect_game_events()
            result = "recorded_only"
            public_event: dict[str, Any] | None = None
            for evt in events:
                evt_dict = evt.to_dict()
                self._record_training_event(evt_dict)
                self.game_event_count += 1
                ep = evt.payload or {}
                print(
                    f"[GAME EVENT] event_type={evt.event_type} target_index={ep.get('target_index')} action={ep.get('action_name')} hit={ep.get('hit')}",
                    flush=True,
                )
                if not evt.reportable:
                    # Keep target_spawn/score_update/target_omitted in the training
                    # log, but do not let them overwrite the user-action event shown
                    # to GUI tests or sent to the platform adapter.
                    continue
                self._set_public_last_game_event(evt_dict)
                public_event = evt_dict
                platform_res = self._platform_adapter.process_game_event(evt_dict, allow_mock=True)
                result = str(platform_res.get("platform_result") or result)
            self.last_game_view = asdict(self._client.build_game_view())
            if self.interaction_enabled and self.session_type == "training":
                self._training_samples.append(self._snapshot_behavior_sample("pointer_click"))
            game_view = dict(self.last_game_view)
            last_game_event = dict(public_event or self.last_game_event)
            game_event_count = self.game_event_count
            platform_message_count = self._platform_adapter.platform_message_count
            last_platform_message = dict(self._platform_adapter.last_platform_message)
            last_platform_result = self._platform_adapter.last_platform_result
        return {"result": result, "status": "accepted", "reason": result, "source": "live_control", "game_input": ge.to_dict(), "last_game_event": last_game_event, "game_event_count": game_event_count, "platform_message_count": platform_message_count, "last_platform_message": last_platform_message, "last_platform_result": last_platform_result, "game_view": game_view}

    def get_runtime_snapshot(self) -> dict[str, Any]:
        rt = self._live_source.get_runtime_snapshot()
        with self._lock:
            rt.update({"source": "live_control", "game_update_count": self.game_update_count, "last_runtime_attention": self.last_runtime_attention, "last_runtime_attention_fresh": self.last_runtime_attention_fresh, "last_runtime_gyro_fresh": self.last_runtime_gyro_fresh, "interaction_enabled": self.interaction_enabled, "live_debug_session_id": self.live_debug_session_id or "", "game_event_count": self.game_event_count})
        return rt

    def get_app_state(self) -> dict[str, Any]:
        base = self._live_source.get_app_state()
        base.update({"source": "live_control", "current_user_id": self.user_id, "current_game_id": self.game_id, "session_active": self.interaction_enabled, "allowed_commands": ["refresh_snapshot", "load_demo_user", "start_mock_session", "start_training_session", "end_training_session", "end_session", "open_last_report", "set_debug_difficulty"]})
        return base

    def get_session_state(self) -> dict[str, Any]:
        sid = (self.training_session_id if self.session_type == "training" else self.live_debug_session_id) or self.last_session_id or ""
        report_path = self._training_context.get("report_path") or self.last_report_path or ""
        log_path = f"logs/sessions/{sid}.jsonl" if sid else ""
        hud = self._current_game_hud()
        latest_decision = self._difficulty_decisions[-1] if self._difficulty_decisions else {}
        latest_changed = next((d for d in reversed(self._difficulty_decisions) if d.get("applied")), {})
        return {"session_id": sid, "session_type": self.session_type or "none", "training_status": self.last_training_status, "latest_session_id": self.last_session_id, "latest_report_path": report_path, "user_id": self.user_id, "game_id": self.game_id, "session_active": self.interaction_enabled, "score": self.last_game_view.get("score", 0), "warning_count": 0, "error_count": 0, "log_path": log_path, "report_path": report_path, "platform_report_status": "mock_only", "source": "live_control", "difficulty_mode": self._difficulty_mode, "debug_difficulty": self._debug_difficulty_level if self._debug_difficulty_level is not None else "auto", "effective_level": hud.get("effective_level", hud.get("level")), "dynamic_difficulty_enabled": hud.get("dynamic_difficulty_enabled"), "dda_enabled": bool((self._dda_state or {}).get("enabled", True)), "dda_mode": ("manual" if self._difficulty_mode == "manual" else "auto"), "latest_difficulty_decision": latest_decision, "latest_difficulty_changed": latest_changed, "dda_applied_count": sum(1 for d in self._difficulty_decisions if d.get("applied")), "game_duration_ms": hud.get("game_duration_ms"), "elapsed_ms": hud.get("elapsed_ms"), "time_left_ms": hud.get("time_left_ms"), "game_completed": hud.get("game_completed")}

    def get_game_view(self) -> dict[str, Any]:
        now_ms = int(time.time() * 1000)
        view = dict(self.last_game_view)
        hints = dict(view.get("layout_hints") or {})
        built_ms = int(hints.get("backend_view_built_wall_ms") or 0)
        hints.update(
            {
                "backend_get_game_view_wall_ms": now_ms,
                "backend_view_age_at_get_ms": (max(0, now_ms - built_ms) if built_ms > 0 else -1),
                "backend_game_update_count_at_get": int(self.game_update_count),
            }
        )
        view["layout_hints"] = hints
        hud = dict(view.get("hud") or {})
        hud["dda_enabled"] = bool((self._dda_state or {}).get("enabled", True))
        hud["external_training_control_enabled"] = bool(getattr(self._client, "_external_training_control_enabled", False))
        view["hud"] = hud
        return view

    def _normalize_debug_difficulty_level(self, level: Any) -> int | None:
        """Normalize difficulty payloads from QML/action/command paths."""
        if level is None:
            return None
        if isinstance(level, str):
            normalized = level.strip().lower()
            if normalized in {"", "auto", "dynamic", "none", "null", "nan"}:
                return None
            level = normalized
        return max(1, min(5, int(level)))

    def set_debug_difficulty(self, level: Any | None) -> dict[str, Any]:
        if self.game_id != "trace_lock":
            return {"command": "set_debug_difficulty", "accepted": True, "status": "unsupported_game", "message": "unsupported_game", "result": "noop", "source": "live_control"}
        if not hasattr(self._client, "set_debug_difficulty"):
            return {"command": "set_debug_difficulty", "accepted": False, "status": "rejected", "message": "unsupported_client", "result": "rejected", "source": "live_control"}
        try:
            self._debug_difficulty_level = self._normalize_debug_difficulty_level(level)
        except (TypeError, ValueError):
            return {"command": "set_debug_difficulty", "accepted": False, "status": "rejected", "message": "invalid_difficulty_level", "result": "rejected", "source": "live_control", "raw_level": level}
        self._difficulty_mode = "auto" if self._debug_difficulty_level is None else "manual"
        self._client.set_debug_difficulty(self._debug_difficulty_level)
        self.last_game_view = asdict(self._client.build_game_view())
        if self.interaction_enabled and self.session_type == "training":
            self._training_samples.append(self._snapshot_behavior_sample("set_debug_difficulty"))
        hud = dict(self.last_game_view.get("hud") or {})
        hud["difficulty_mode"] = self._difficulty_mode
        hud["debug_difficulty"] = self._debug_difficulty_level if self._debug_difficulty_level is not None else "auto"
        hud["dynamic_difficulty_enabled"] = self._debug_difficulty_level is None
        hud["dda_enabled"] = bool((self._dda_state or {}).get("enabled", True))
        hud["external_training_control_enabled"] = bool(getattr(self._client, "_external_training_control_enabled", False))
        view = dict(self.last_game_view)
        view["hud"] = hud
        self.last_game_view = view
        print(
            f"[GAME DIFFICULTY] mode={self._difficulty_mode} debug_difficulty={self._debug_difficulty_level if self._debug_difficulty_level is not None else 'auto'} effective_level={hud.get('effective_level', hud.get('level'))} running={self.interaction_enabled}",
            flush=True,
        )
        return {
            "command": "set_debug_difficulty",
            "accepted": True,
            "status": "accepted",
            "message": "debug_difficulty_set",
            "result": "accepted",
            "source": "live_control",
            "level": hud.get("effective_level", hud.get("level", self._debug_difficulty_level if self._debug_difficulty_level is not None else "auto")),
            "difficulty_mode": self._difficulty_mode,
            "debug_difficulty": self._debug_difficulty_level if self._debug_difficulty_level is not None else "auto",
            "dynamic_difficulty_enabled": self._debug_difficulty_level is None,
            "effective_level": hud.get("effective_level", hud.get("level")),
            "dda_enabled": bool((self._dda_state or {}).get("enabled", True)),
            "game_hud": hud,
            "raw_level": level,
        }
