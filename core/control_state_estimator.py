from __future__ import annotations


class ControlStateEstimator:
    def __init__(self):
        self._state = "UNRELIABLE_SIGNAL"
        self._dwell_ms = 0
        self._high_focus_streak = 0

    def evaluate(self, runtime_snapshot: dict, fi_result: dict, tick_ms: int = 50) -> dict:
        reason = "fi_based"
        if not runtime_snapshot.get("estimation_allowed", False):
            state = "UNRELIABLE_SIGNAL"
            reason = "estimation_not_allowed"
        elif not fi_result.get("fi_valid", False):
            state = "UNRELIABLE_SIGNAL"
            reason = "fi_invalid"
        elif runtime_snapshot.get("quality_state") == "warning" or fi_result.get("fi_confidence") == "low":
            state = "LOW_CONFIDENCE"
            reason = "quality_warning"
        else:
            fi = float(fi_result.get("fi_smoothed", 0.0))
            s_imu = fi_result.get("s_imu")
            if fi >= 80:
                self._high_focus_streak += 1
                state = "HIGH_FOCUS" if self._high_focus_streak >= 2 else "STABLE_FOCUS"
                reason = "high_focus_confirmed" if state == "HIGH_FOCUS" else "high_focus_waiting"
            else:
                self._high_focus_streak = 0
                if fi >= 60:
                    state = "STABLE_FOCUS"
                elif fi >= 40:
                    state = "DISTRACTED"
                else:
                    state = "FATIGUED" if (s_imu is not None and s_imu < 0.2) else "DISTRACTED"
                    reason = "fatigue_conservative" if state == "FATIGUED" else "low_fi"
        if state == self._state:
            self._dwell_ms += tick_ms
        else:
            self._state = state
            self._dwell_ms = tick_ms
        return {"control_state": self._state, "control_state_reason": reason, "control_state_dwell_ms": self._dwell_ms}
