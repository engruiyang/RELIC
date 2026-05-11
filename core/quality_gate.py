from __future__ import annotations


class QualityGate:
    def evaluate(
        self,
        runtime_snapshot: dict,
        current_user: dict | None,
        user_profile: dict | None,
        bound_calibration_profile: dict | None,
        warning_flags: list[str] | None = None,
        error_flags: list[str] | None = None,
    ) -> dict:
        reasons: list[str] = []
        warning_flags = warning_flags or []
        error_flags = error_flags or []
        quality_state = "ok"
        signal_reliable = True
        calibration_usable = False
        formal_training_allowed = False
        estimation_allowed = False

        if current_user is None:
            reasons.append("no_user")
        if user_profile is None:
            reasons.append("no_profile")
        else:
            last_calibration_id = user_profile.get("last_calibration_id")
            if not last_calibration_id:
                reasons.append("no_calibration")
            elif bound_calibration_profile is None:
                reasons.append("calibration_binding_inconsistent")
            elif not bool(bound_calibration_profile.get("valid")):
                reasons.append("calibration_invalid")
            elif bound_calibration_profile.get("calibration_id") != last_calibration_id:
                reasons.append("calibration_binding_inconsistent")
            else:
                calibration_usable = True
                estimation_allowed = True
                source = "mock" if bound_calibration_profile.get("device_id") == "mock_device" else "ipc"
                if source == "mock":
                    reasons.append("mock_calibration_debug_only")
                    formal_training_allowed = False
                else:
                    formal_training_allowed = True
                if bound_calibration_profile.get("attention_std") == 0:
                    reasons.append("attention_std_zero_fallback_required")
                if runtime_snapshot.get("baseline_confidence") == "low":
                    reasons.append("low_baseline_confidence")
                    formal_training_allowed = False
                    quality_state = "warning"

        severe = {"attention_lost", "gyro_lost"}
        if severe.intersection(error_flags):
            quality_state = "error"
            signal_reliable = False
            estimation_allowed = False
            reasons.extend(sorted(severe.intersection(error_flags)))
        elif "attention_stale" in warning_flags or "gyro_stale" in warning_flags:
            quality_state = "warning"
            signal_reliable = False
            reasons.extend([x for x in ("attention_stale", "gyro_stale") if x in warning_flags])
        elif "attention_missing" in warning_flags or "gyro_missing" in warning_flags:
            quality_state = "warning"
            formal_training_allowed = False
            reasons.extend([x for x in ("attention_missing", "gyro_missing") if x in warning_flags])

        if any(x in reasons for x in ("no_user", "no_profile", "no_calibration", "calibration_binding_inconsistent", "calibration_invalid")):
            quality_state = "error"
            calibration_usable = False
            formal_training_allowed = False
            estimation_allowed = False

        if quality_state == "error":
            sqi = 0.3
        elif quality_state == "warning":
            sqi = 0.65
        else:
            sqi = 0.9
        return {
            "sqi": sqi,
            "quality_state": quality_state,
            "quality_reasons": sorted(set(reasons)),
            "calibration_usable": calibration_usable,
            "formal_training_allowed": formal_training_allowed,
            "signal_reliable": signal_reliable,
            "estimation_allowed": estimation_allowed,
        }
