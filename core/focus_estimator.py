from __future__ import annotations

import math
from collections import deque


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


class FocusEstimator:
    def __init__(self, alpha: float = 0.85):
        self.alpha = alpha
        self._last_fi_smoothed: float | None = None
        self._gyro_window: deque[tuple[float, float, float]] = deque(maxlen=20)

    def estimate(self, runtime_snapshot: dict, user_profile: dict | None, calibration_profile: dict | None) -> dict:
        reasons: list[str] = []
        s_b = 0.60
        s_b_source = "neutral_default"
        behavior_ready = False
        reasons.append("behavior_score_default")
        behavior_sample = runtime_snapshot.get("behavior_sample")
        if isinstance(behavior_sample, dict):
            acc = behavior_sample.get("accuracy")
            om = behavior_sample.get("omission")
            fa = behavior_sample.get("false_action")
            rt = behavior_sample.get("rt_stability")
            if acc is None and behavior_sample.get("target_count") is not None:
                t = max(float(behavior_sample.get("target_count", 0)), 1.0)
                acc = float(behavior_sample.get("correct_count", 0.0)) / t
                om = float(behavior_sample.get("omission_count", 0.0)) / t
                fa = float(behavior_sample.get("false_action_count", 0.0)) / max(float(behavior_sample.get("action_count", 0.0)), 1.0)
                rt = 0.5
            if None not in (acc, om, fa, rt):
                s_b = _clamp(0.35 * float(acc) + 0.20 * (1 - float(om)) + 0.15 * (1 - float(fa)) + 0.30 * float(rt), 0.0, 1.0)
                s_b_source = "behavior_sample"
                behavior_ready = True
                reasons = [r for r in reasons if r != "behavior_score_default"]
        if not runtime_snapshot.get("estimation_allowed", False):
            reasons.append("estimation_not_allowed")
            return {"s_eeg": None, "s_imu": None, "s_b": s_b, "s_b_source": s_b_source, "behavior_ready": behavior_ready, "attention_normalization_method": None, "motion_energy": None, "fi_raw": None, "fi_smoothed": self._last_fi_smoothed, "fi_valid": False, "fi_confidence": "low", "fi_reasons": reasons + ["fi_invalid_no_update"]}

        if not runtime_snapshot.get("attention_fresh", False):
            reasons.append("attention_not_fresh")
            return {"s_eeg": None, "s_imu": None, "s_b": s_b, "s_b_source": s_b_source, "behavior_ready": behavior_ready, "attention_normalization_method": None, "motion_energy": None, "fi_raw": None, "fi_smoothed": self._last_fi_smoothed, "fi_valid": False, "fi_confidence": "low", "fi_reasons": reasons + ["fi_hold_last_valid"]}
        if not runtime_snapshot.get("gyro_fresh", False):
            reasons.append("gyro_not_fresh")
            return {"s_eeg": None, "s_imu": None, "s_b": s_b, "s_b_source": s_b_source, "behavior_ready": behavior_ready, "attention_normalization_method": None, "motion_energy": None, "fi_raw": None, "fi_smoothed": self._last_fi_smoothed, "fi_valid": False, "fi_confidence": "low", "fi_reasons": reasons + ["fi_hold_last_valid"]}

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
                low_f = float(low)
                high_f = float(high)
                if attention <= low_f:
                    s_eeg = _clamp(0.1 * (attention / max(low_f, 1.0)), 0.0, 0.1)
                elif attention <= high_f:
                    s_eeg = _clamp(0.1 + 0.8 * ((attention - low_f) / max(high_f - low_f, 1e-6)), 0.1, 0.9)
                else:
                    s_eeg = _clamp(0.9 + 0.1 * ((attention - high_f) / max(high_f, 1.0)), 0.9, 1.0)
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
        self._gyro_window.append((gx, gy, gz))
        noise = 0.0 if calibration_profile is None or calibration_profile.get("gyro_noise_rms") is None else float(calibration_profile.get("gyro_noise_rms"))
        if noise <= 0:
            noise = 0.5
            reasons.append("gyro_noise_zero_fallback")
        p_rate = 0.0
        p_jitter = 0.0
        p_offset = 0.0
        if len(self._gyro_window) < 5:
            s_imu = 0.6
            reasons.append("imu_short_window_fallback")
            gyro_rate_rms = 0.0
            gyro_jitter_rms = 0.0
        else:
            deltas = []
            prev = None
            for cur in self._gyro_window:
                if prev is not None:
                    deltas.append(math.sqrt((cur[0] - prev[0]) ** 2 + (cur[1] - prev[1]) ** 2 + (cur[2] - prev[2]) ** 2))
                prev = cur
            mean_delta = sum(deltas) / max(len(deltas), 1)
            gyro_rate_rms = mean_delta
            medx = sorted(v[0] for v in self._gyro_window)[len(self._gyro_window)//2]
            medy = sorted(v[1] for v in self._gyro_window)[len(self._gyro_window)//2]
            medz = sorted(v[2] for v in self._gyro_window)[len(self._gyro_window)//2]
            gyro_jitter_rms = math.sqrt(sum(((v[0]-medx)**2 + (v[1]-medy)**2 + (v[2]-medz)**2) / 3.0 for v in self._gyro_window) / len(self._gyro_window))
            rate_soft = max(5 * noise, 1.5)
            rate_bad = max(20 * noise, 6.0)
            jitter_soft = max(3 * noise, 0.8)
            jitter_bad = max(10 * noise, 3.0)
            p_rate = _clamp((gyro_rate_rms - rate_soft) / max(rate_bad - rate_soft, 1e-6), 0.0, 1.0)
            p_jitter = _clamp((gyro_jitter_rms - jitter_soft) / max(jitter_bad - jitter_soft, 1e-6), 0.0, 1.0)
            p_offset = _clamp((motion_energy - 15.0) / 30.0, 0.0, 1.0)
            stability = _clamp(1.0 - (0.55 * p_rate + 0.35 * p_jitter), 0.0, 1.0)
            bias_penalty = 0.10 * p_offset
            s_imu = _clamp(stability - bias_penalty, 0.0, 1.0)
        fi_raw = 100.0 * (0.55 * s_eeg + 0.15 * s_imu + 0.30 * s_b)
        fi_smoothed = fi_raw if self._last_fi_smoothed is None else (self.alpha * self._last_fi_smoothed + (1.0 - self.alpha) * fi_raw)
        self._last_fi_smoothed = fi_smoothed
        conf = "high"
        if runtime_snapshot.get("quality_state") == "warning":
            conf = "low"
        elif "attention_std_zero_fallback" in reasons:
            conf = "medium"
        if "behavior_score_default" in reasons and conf == "high":
            conf = "medium"
        if "imu_short_window_fallback" in reasons and conf == "high":
            conf = "medium"
        return {"s_eeg": s_eeg, "s_imu": s_imu, "s_b": s_b, "s_b_source": s_b_source, "behavior_ready": behavior_ready, "attention_normalization_method": norm, "motion_energy": motion_energy, "gyro_rate_rms": gyro_rate_rms, "gyro_jitter_rms": gyro_jitter_rms, "gyro_offset_rms": motion_energy, "p_rate": p_rate, "p_jitter": p_jitter, "p_offset": p_offset, "fi_raw": _clamp(fi_raw, 0.0, 100.0), "fi_smoothed": _clamp(fi_smoothed, 0.0, 100.0), "fi_valid": True, "fi_confidence": conf, "fi_reasons": sorted(set(reasons))}
