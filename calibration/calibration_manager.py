from __future__ import annotations

import math
import time
import uuid
from datetime import datetime, timezone
from statistics import median
from typing import Callable

from calibration.calibration_profile import CalibrationProfile


class CalibrationManager:
    def __init__(self, store=None, profile_manager=None, min_valid_ratio: float = 0.7, gyro_noise_rms_threshold: float = 1.2, attention_shift_threshold: float = 30.0):
        self.store = store
        self.profile_manager = profile_manager
        self.min_valid_ratio = min_valid_ratio
        self.gyro_noise_rms_threshold = gyro_noise_rms_threshold
        self.attention_shift_threshold = attention_shift_threshold

    def start_calibration(
        self,
        user: dict,
        calibration_type: str,
        gyro_snapshots: list[dict],
        attention_snapshots: list[dict],
        *,
        fast: bool = True,
        emit_event: Callable[[dict], None] | None = None,
    ) -> CalibrationProfile:
        if self.store is None:
            raise ValueError("store is required")
        history = self.list_calibrations(user["user_id"]) if user["user_type"] != "guest" else []
        has_history = bool(history)
        resolved_type = "quick_check" if calibration_type == "auto" and has_history else ("first_profile" if calibration_type == "auto" else calibration_type)
        pending_id = f"pending_{uuid.uuid4().hex[:10]}"
        phase_names = ["preparation", "gyro_static_baseline", "attention_quick_baseline", "result"]
        phase_count = len(phase_names)
        phase_ms = 200 if fast else 2500
        t0 = time.monotonic()

        def emit(event_type: str, phase: str, phase_index: int, progress: float, collected: int = 0, vatt: int = 0, vgyro: int = 0, message: str = ""):
            if emit_event is None:
                return
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            total_ms = phase_ms * phase_count
            emit_event(
                {
                    "event_type": event_type,
                    "pending_calibration_id": pending_id,
                    "user_id": user["user_id"],
                    "calibration_type": resolved_type,
                    "phase": phase,
                    "phase_index": phase_index,
                    "phase_count": phase_count,
                    "progress": progress,
                    "elapsed_ms": elapsed_ms,
                    "remaining_ms": max(0, total_ms - elapsed_ms),
                    "collected_samples": collected,
                    "valid_attention_samples": vatt,
                    "valid_gyro_samples": vgyro,
                    "message": message,
                    "cancellable": True,
                }
            )

        emit("calibration_started", phase_names[0], 1, 0.0, message="calibration started")
        for i, phase in enumerate(phase_names, start=1):
            emit("calibration_phase_started", phase, i, (i - 1) / phase_count, message=f"phase started: {phase}")
            steps = 1 if fast else 3
            for s in range(steps):
                if not fast:
                    time.sleep(phase_ms / steps / 1000.0)
                emit(
                    "calibration_progress",
                    phase,
                    i,
                    min(0.99, ((i - 1) + (s + 1) / steps) / phase_count),
                    collected=int((len(gyro_snapshots) + len(attention_snapshots)) * ((i - 1) + (s + 1) / steps) / phase_count),
                    vatt=sum(1 for x in attention_snapshots if x.get("attention_fresh") and not x.get("error_flags") and x.get("attention") is not None),
                    vgyro=sum(1 for x in gyro_snapshots if x.get("gyro_fresh") and not x.get("error_flags") and x.get("gyro_x") is not None),
                    message=f"phase progress: {phase}",
                )
            emit("calibration_phase_completed", phase, i, i / phase_count, message=f"phase completed: {phase}")

        historical_baseline = history[-1].get("attention_baseline") if history else None
        cp = self.run_quick_calibration(user_id=user["user_id"], user_type=user["user_type"], device_id="mock_device", gyro_snapshots=gyro_snapshots, attention_snapshots=attention_snapshots, has_history=(resolved_type == "quick_check"), historical_baseline=historical_baseline)
        cp.calibration_type = resolved_type

        if cp.valid:
            emit("calibration_completed", "result", phase_count, 1.0, message="calibration completed")
        else:
            emit("calibration_failed", "result", phase_count, 1.0, message=cp.failure_reason or "calibration failed")

        if user["user_type"] != "guest":
            self.store.save_calibration_profile(cp.to_dict())
            if cp.valid and self.profile_manager is not None:
                self.profile_manager.update_last_calibration_id(user["user_id"], cp.calibration_id)
        return cp

    def cancel_calibration(self, user: dict, reason: str = "cancelled_by_user") -> CalibrationProfile:
        return CalibrationProfile(calibration_id=f"cal_{uuid.uuid4().hex[:12]}", user_id=user["user_id"], device_id="mock_device", created_at=datetime.now(timezone.utc).isoformat(), calibration_type="triggered", attention_baseline=None, attention_std=None, attention_valid_sample_ratio=0.0, gyro_bias_x=None, gyro_bias_y=None, gyro_bias_z=None, gyro_noise_x=None, gyro_noise_y=None, gyro_noise_z=None, gyro_noise_rms=None, gyro_stability_score=0.0, signal_quality_baseline=0.0, valid=False, failure_reason=reason, non_persistent=True)

    def get_latest_calibration(self, user_id: str) -> dict | None:
        return None if self.store is None else self.store.get_latest_calibration_profile(user_id)

    def list_calibrations(self, user_id: str) -> list[dict]: return [] if self.store is None else self.store.list_calibration_profiles(user_id)
    def get_calibration(self, calibration_id: str) -> dict | None: return None if self.store is None else self.store.get_calibration_profile(calibration_id)

    def bind_calibration_to_profile(self, user_id: str, calibration_id: str) -> tuple[str | None, str]:
        if self.profile_manager is None: raise ValueError("profile_manager is required")
        cp = self.get_calibration(calibration_id)
        if cp is None: raise ValueError("calibration_not_found")
        if cp["user_id"] != user_id: raise ValueError("calibration_user_mismatch")
        if not bool(cp["valid"]): raise ValueError("invalid_calibration")
        old = self.profile_manager.get_profile(user_id).get("last_calibration_id")
        new = self.profile_manager.update_last_calibration_id(user_id, calibration_id)["last_calibration_id"]
        return old, new

    def get_calibration_status(self, user_id: str) -> dict:
        latest = self.get_latest_calibration(user_id)
        profile = self.profile_manager.get_profile(user_id) if self.profile_manager else None
        bound_id = None if profile is None else profile.get("last_calibration_id")
        bound_exists = bool(bound_id and self.get_calibration(bound_id))
        return {"profile_loaded": profile is not None, "profile.last_calibration_id": bound_id, "bound_calibration_exists": bound_exists, "latest_calibration_id": None if latest is None else latest["calibration_id"], "latest_calibration_type": None if latest is None else latest["calibration_type"], "latest_valid": None if latest is None else bool(latest["valid"]) }

    def run_quick_calibration(self, *, user_id: str, user_type: str, device_id: str, gyro_snapshots: list[dict], attention_snapshots: list[dict], has_history: bool, historical_baseline: float | None) -> CalibrationProfile:
        calibration_type = "quick_check" if has_history else "first_profile"
        valid, failure_reason, metrics = self._compute_metrics(gyro_snapshots, attention_snapshots, historical_baseline)
        return CalibrationProfile(calibration_id=f"cal_{uuid.uuid4().hex[:12]}", user_id=user_id, device_id=device_id, created_at=datetime.now(timezone.utc).isoformat(), calibration_type=calibration_type, attention_baseline=metrics["attention_baseline"], attention_std=metrics["attention_std"], attention_valid_sample_ratio=metrics["attention_valid_sample_ratio"], gyro_bias_x=metrics["gyro_bias_x"], gyro_bias_y=metrics["gyro_bias_y"], gyro_bias_z=metrics["gyro_bias_z"], gyro_noise_x=metrics["gyro_noise_x"], gyro_noise_y=metrics["gyro_noise_y"], gyro_noise_z=metrics["gyro_noise_z"], gyro_noise_rms=metrics["gyro_noise_rms"], gyro_stability_score=metrics["gyro_stability_score"], signal_quality_baseline=metrics["signal_quality_baseline"], valid=valid, failure_reason=failure_reason, non_persistent=(user_type == "guest"))

    def _compute_metrics(self, gyro_snapshots: list[dict], attention_snapshots: list[dict], historical_baseline: float | None):
        def mad(values: list[float], med: float) -> float: return 1.4826 * median([abs(v - med) for v in values])
        valid_gyro = [s for s in gyro_snapshots if s.get("gyro_fresh") and not s.get("error_flags") and s.get("gyro_x") is not None]
        gyro_ratio = len(valid_gyro) / max(len(gyro_snapshots), 1)
        if gyro_ratio < self.min_valid_ratio: return False, "insufficient_valid_samples", self._empty_metrics(gyro_ratio, 0.0)
        gx, gy, gz = [float(s["gyro_x"]) for s in valid_gyro], [float(s["gyro_y"]) for s in valid_gyro], [float(s["gyro_z"]) for s in valid_gyro]
        bx, by, bz = median(gx), median(gy), median(gz)
        nx, ny, nz = mad(gx, bx), mad(gy, by), mad(gz, bz)
        nrms = math.sqrt((nx * nx + ny * ny + nz * nz) / 3.0)
        if nrms > self.gyro_noise_rms_threshold: return False, "gyro_unstable", self._empty_metrics(gyro_ratio, 0.0) | {"gyro_bias_x": bx, "gyro_bias_y": by, "gyro_bias_z": bz, "gyro_noise_x": nx, "gyro_noise_y": ny, "gyro_noise_z": nz, "gyro_noise_rms": nrms, "gyro_stability_score": max(0.0, 1.0 - nrms / self.gyro_noise_rms_threshold)}
        valid_att = [s for s in attention_snapshots if s.get("attention_fresh") and not s.get("error_flags") and s.get("attention") is not None]
        att_ratio = len(valid_att) / max(len(attention_snapshots), 1)
        if att_ratio < self.min_valid_ratio: return False, "insufficient_valid_samples", self._empty_metrics(gyro_ratio, att_ratio)
        av = [float(s["attention"]) for s in valid_att]
        if not av or all(v == 0 for v in av): return False, "attention_lost", self._empty_metrics(gyro_ratio, att_ratio)
        abaseline, astd = median(av), mad(av, median(av))
        if historical_baseline is not None and abs(abaseline - historical_baseline) > self.attention_shift_threshold: return False, "attention_baseline_shift", self._empty_metrics(gyro_ratio, att_ratio) | {"attention_baseline": abaseline, "attention_std": astd}
        return True, None, {"attention_baseline": abaseline, "attention_std": astd, "attention_valid_sample_ratio": att_ratio, "gyro_bias_x": bx, "gyro_bias_y": by, "gyro_bias_z": bz, "gyro_noise_x": nx, "gyro_noise_y": ny, "gyro_noise_z": nz, "gyro_noise_rms": nrms, "gyro_stability_score": max(0.0, 1.0 - nrms / self.gyro_noise_rms_threshold), "signal_quality_baseline": min(gyro_ratio, att_ratio)}

    def _empty_metrics(self, gyro_ratio: float, att_ratio: float) -> dict:
        return {"attention_baseline": None, "attention_std": None, "attention_valid_sample_ratio": att_ratio, "gyro_bias_x": None, "gyro_bias_y": None, "gyro_bias_z": None, "gyro_noise_x": None, "gyro_noise_y": None, "gyro_noise_z": None, "gyro_noise_rms": None, "gyro_stability_score": 0.0, "signal_quality_baseline": min(gyro_ratio, att_ratio)}
