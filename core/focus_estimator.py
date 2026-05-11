from __future__ import annotations

import math


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


class FocusEstimator:
    def __init__(self, alpha: float = 0.85):
        self.alpha = alpha
        self._last_fi_smoothed: float | None = None

    def estimate(self, runtime_snapshot: dict, user_profile: dict | None, calibration_profile: dict | None) -> dict:
        reasons: list[str] = []
        s_b = 0.5
        s_b_source = "neutral_default"
        reasons.append("behavior_score_default")
        if not runtime_snapshot.get("estimation_allowed", False):
            reasons.append("estimation_not_allowed")
            return {"s_eeg": None, "s_imu": None, "s_b": s_b, "s_b_source": s_b_source, "attention_normalization_method": None, "motion_energy": None, "fi_raw": None, "fi_smoothed": self._last_fi_smoothed, "fi_valid": False, "fi_confidence": "low", "fi_reasons": reasons + ["fi_invalid_no_update"]}

        if not runtime_snapshot.get("attention_fresh", False):
            reasons.append("attention_not_fresh")
            return {"s_eeg": None, "s_imu": None, "s_b": s_b, "s_b_source": s_b_source, "attention_normalization_method": None, "motion_energy": None, "fi_raw": None, "fi_smoothed": self._last_fi_smoothed, "fi_valid": False, "fi_confidence": "low", "fi_reasons": reasons + ["fi_hold_last_valid"]}
        if not runtime_snapshot.get("gyro_fresh", False):
            reasons.append("gyro_not_fresh")
            return {"s_eeg": None, "s_imu": None, "s_b": s_b, "s_b_source": s_b_source, "attention_normalization_method": None, "motion_energy": None, "fi_raw": None, "fi_smoothed": self._last_fi_smoothed, "fi_valid": False, "fi_confidence": "low", "fi_reasons": reasons + ["fi_hold_last_valid"]}

        attention = float(runtime_snapshot.get("attention", 0.0))
        baseline = None if calibration_profile is None else calibration_profile.get("attention_baseline")
        std = None if calibration_profile is None else calibration_profile.get("attention_std")
        if std is not None and std > 0 and baseline is not None:
            z = (attention - float(baseline)) / float(std)
            s_eeg = 1.0 / (1.0 + math.exp(-z))
            norm = "z_score"
        else:
            low = None if user_profile is None else user_profile.get("attention_low_threshold")
            high = None if user_profile is None else user_profile.get("attention_high_threshold")
            if low is not None and high is not None and high > low:
                s_eeg = _clamp((attention - float(low)) / float(high - low), 0.0, 1.0)
                norm = "profile_threshold_fallback"
            else:
                b = float(baseline if baseline is not None else attention)
                s_eeg = _clamp((attention - (b - 15.0)) / 30.0, 0.0, 1.0)
                norm = "baseline_window_fallback"
            reasons.append("attention_std_zero_fallback")

        gx, gy, gz = (runtime_snapshot.get("gyro_x"), runtime_snapshot.get("gyro_y"), runtime_snapshot.get("gyro_z"))
        bx = 0.0 if calibration_profile is None or calibration_profile.get("gyro_bias_x") is None else float(calibration_profile.get("gyro_bias_x"))
        by = 0.0 if calibration_profile is None or calibration_profile.get("gyro_bias_y") is None else float(calibration_profile.get("gyro_bias_y"))
        bz = 0.0 if calibration_profile is None or calibration_profile.get("gyro_bias_z") is None else float(calibration_profile.get("gyro_bias_z"))
        gx = float(gx if gx is not None else bx)
        gy = float(gy if gy is not None else by)
        gz = float(gz if gz is not None else bz)
        motion_energy = math.sqrt((gx - bx) ** 2 + (gy - by) ** 2 + (gz - bz) ** 2)
        noise = 0.0 if calibration_profile is None or calibration_profile.get("gyro_noise_rms") is None else float(calibration_profile.get("gyro_noise_rms"))
        if noise <= 0:
            noise = 1e-3
            reasons.append("gyro_noise_zero_fallback")
        s_imu = _clamp(1.0 - motion_energy / (3.0 * noise), 0.0, 1.0)
        fi_raw = 100.0 * (0.55 * s_eeg + 0.15 * s_imu + 0.30 * s_b)
        fi_smoothed = fi_raw if self._last_fi_smoothed is None else (self.alpha * self._last_fi_smoothed + (1.0 - self.alpha) * fi_raw)
        self._last_fi_smoothed = fi_smoothed
        conf = "high"
        if runtime_snapshot.get("quality_state") == "warning":
            conf = "low"
        elif "attention_std_zero_fallback" in reasons:
            conf = "medium"
        return {"s_eeg": s_eeg, "s_imu": s_imu, "s_b": s_b, "s_b_source": s_b_source, "attention_normalization_method": norm, "motion_energy": motion_energy, "fi_raw": _clamp(fi_raw, 0.0, 100.0), "fi_smoothed": _clamp(fi_smoothed, 0.0, 100.0), "fi_valid": True, "fi_confidence": conf, "fi_reasons": sorted(set(reasons))}
