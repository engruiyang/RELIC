from __future__ import annotations

import math
import uuid
from datetime import datetime, timezone
from statistics import median

from calibration.calibration_profile import CalibrationProfile


class CalibrationManager:
    def __init__(
        self,
        min_valid_ratio: float = 0.7,
        gyro_noise_rms_threshold: float = 1.2,
        attention_shift_threshold: float = 30.0,
    ):
        self.min_valid_ratio = min_valid_ratio
        self.gyro_noise_rms_threshold = gyro_noise_rms_threshold
        self.attention_shift_threshold = attention_shift_threshold

    def run_quick_calibration(
        self,
        *,
        user_id: str,
        user_type: str,
        device_id: str,
        gyro_snapshots: list[dict],
        attention_snapshots: list[dict],
        has_history: bool,
        historical_baseline: float | None,
    ) -> CalibrationProfile:
        calibration_type = "quick_check" if has_history else "first_profile"
        valid, failure_reason, metrics = self._compute_metrics(gyro_snapshots, attention_snapshots, historical_baseline)
        return CalibrationProfile(
            calibration_id=f"cal_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            device_id=device_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            calibration_type=calibration_type,
            attention_baseline=metrics["attention_baseline"],
            attention_std=metrics["attention_std"],
            attention_valid_sample_ratio=metrics["attention_valid_sample_ratio"],
            gyro_bias_x=metrics["gyro_bias_x"],
            gyro_bias_y=metrics["gyro_bias_y"],
            gyro_bias_z=metrics["gyro_bias_z"],
            gyro_noise_x=metrics["gyro_noise_x"],
            gyro_noise_y=metrics["gyro_noise_y"],
            gyro_noise_z=metrics["gyro_noise_z"],
            gyro_noise_rms=metrics["gyro_noise_rms"],
            gyro_stability_score=metrics["gyro_stability_score"],
            signal_quality_baseline=metrics["signal_quality_baseline"],
            valid=valid,
            failure_reason=failure_reason,
            non_persistent=(user_type == "guest"),
        )

    def _compute_metrics(self, gyro_snapshots: list[dict], attention_snapshots: list[dict], historical_baseline: float | None):
        def mad(values: list[float], med: float) -> float:
            return 1.4826 * median([abs(v - med) for v in values])

        valid_gyro = [
            s for s in gyro_snapshots
            if s.get("gyro_fresh") and not s.get("error_flags") and s.get("gyro_x") is not None
        ]
        gyro_ratio = len(valid_gyro) / max(len(gyro_snapshots), 1)
        if gyro_ratio < self.min_valid_ratio:
            return False, "insufficient_valid_samples", self._empty_metrics(gyro_ratio, 0.0)

        gx = [float(s["gyro_x"]) for s in valid_gyro]
        gy = [float(s["gyro_y"]) for s in valid_gyro]
        gz = [float(s["gyro_z"]) for s in valid_gyro]
        bx, by, bz = median(gx), median(gy), median(gz)
        nx, ny, nz = mad(gx, bx), mad(gy, by), mad(gz, bz)
        nrms = math.sqrt((nx * nx + ny * ny + nz * nz) / 3.0)
        if nrms > self.gyro_noise_rms_threshold:
            return False, "gyro_unstable", self._empty_metrics(gyro_ratio, 0.0) | {
                "gyro_bias_x": bx, "gyro_bias_y": by, "gyro_bias_z": bz,
                "gyro_noise_x": nx, "gyro_noise_y": ny, "gyro_noise_z": nz,
                "gyro_noise_rms": nrms, "gyro_stability_score": max(0.0, 1.0 - nrms / self.gyro_noise_rms_threshold),
            }

        valid_att = [
            s for s in attention_snapshots
            if s.get("attention_fresh") and not s.get("error_flags") and s.get("attention") is not None
        ]
        att_ratio = len(valid_att) / max(len(attention_snapshots), 1)
        if att_ratio < self.min_valid_ratio:
            return False, "insufficient_valid_samples", self._empty_metrics(gyro_ratio, att_ratio)

        av = [float(s["attention"]) for s in valid_att]
        if not av or all(v == 0 for v in av):
            return False, "attention_lost", self._empty_metrics(gyro_ratio, att_ratio)

        abaseline = median(av)
        astd = mad(av, abaseline)
        if historical_baseline is not None and abs(abaseline - historical_baseline) > self.attention_shift_threshold:
            return False, "attention_baseline_shift", self._empty_metrics(gyro_ratio, att_ratio) | {
                "attention_baseline": abaseline,
                "attention_std": astd,
            }

        return True, None, {
            "attention_baseline": abaseline,
            "attention_std": astd,
            "attention_valid_sample_ratio": att_ratio,
            "gyro_bias_x": bx,
            "gyro_bias_y": by,
            "gyro_bias_z": bz,
            "gyro_noise_x": nx,
            "gyro_noise_y": ny,
            "gyro_noise_z": nz,
            "gyro_noise_rms": nrms,
            "gyro_stability_score": max(0.0, 1.0 - nrms / self.gyro_noise_rms_threshold),
            "signal_quality_baseline": min(gyro_ratio, att_ratio),
        }

    def _empty_metrics(self, gyro_ratio: float, att_ratio: float) -> dict:
        return {
            "attention_baseline": None,
            "attention_std": None,
            "attention_valid_sample_ratio": att_ratio,
            "gyro_bias_x": None,
            "gyro_bias_y": None,
            "gyro_bias_z": None,
            "gyro_noise_x": None,
            "gyro_noise_y": None,
            "gyro_noise_z": None,
            "gyro_noise_rms": None,
            "gyro_stability_score": 0.0,
            "signal_quality_baseline": min(gyro_ratio, att_ratio),
        }
