from __future__ import annotations


class QualityGate:
    def __init__(self, sqi_ok_threshold: float = 0.75, sqi_invalid_threshold: float = 0.60):
        self.sqi_ok_threshold = sqi_ok_threshold
        self.sqi_invalid_threshold = sqi_invalid_threshold

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

        # SQI core components (Task6B-2)
        att_age = runtime_snapshot.get("attention_age_ms")
        gyro_age = runtime_snapshot.get("gyro_age_ms")
        if "attention_seen_once" not in runtime_snapshot and "attention_age_ms" not in runtime_snapshot:
            q_attention = 1.0
        elif not runtime_snapshot.get("attention_seen_once") or runtime_snapshot.get("attention") is None:
            q_attention = 0.0
            reasons.append("attention_missing")
        elif att_age is not None and att_age <= 1500:
            q_attention = 1.0
        elif att_age is not None and att_age <= 5000:
            q_attention = 1.0 - 0.8 * ((att_age - 1500) / 3500.0)
            reasons.append("attention_stale")
        else:
            q_attention = 0.0
            reasons.append("attention_lost")
            error_flags = list(error_flags) + ["attention_lost"]

        if "gyro_seen_once" not in runtime_snapshot and "gyro_age_ms" not in runtime_snapshot:
            q_gyro = 1.0
        elif not runtime_snapshot.get("gyro_seen_once") or runtime_snapshot.get("gyro_x") is None:
            q_gyro = 0.0
            reasons.append("gyro_missing")
        elif gyro_age is not None and gyro_age <= 500:
            q_gyro = 1.0
        elif gyro_age is not None and gyro_age <= 2000:
            q_gyro = 1.0 - 0.8 * ((gyro_age - 500) / 1500.0)
            reasons.append("gyro_stale")
        else:
            q_gyro = 0.0
            reasons.append("gyro_lost")
            error_flags = list(error_flags) + ["gyro_lost"]

        if "device_connected" not in runtime_snapshot and "stream_alive" not in runtime_snapshot:
            q_stream = 1.0
        elif runtime_snapshot.get("device_connected") and runtime_snapshot.get("stream_alive"):
            q_stream = 1.0 if runtime_snapshot.get("attention_seen_once") and runtime_snapshot.get("gyro_seen_once") else 0.5
        else:
            q_stream = 0.0
            reasons.append("stream_dead")
            error_flags = list(error_flags) + ["stream_dead"]

        q_motion = float(runtime_snapshot.get("q_motion", 1.0))
        sqi = max(0.0, min(1.0, 0.45 * q_attention + 0.25 * q_gyro + 0.20 * q_motion + 0.10 * q_stream))
        quality_state = "ok" if sqi >= self.sqi_ok_threshold else ("warning" if sqi >= self.sqi_invalid_threshold else "invalid")

        severe = {"attention_lost", "gyro_lost", "stream_dead"}
        if severe.intersection(error_flags):
            quality_state = "error"
            signal_reliable = False
            estimation_allowed = False
            formal_training_allowed = False
            reasons.extend(sorted(severe.intersection(error_flags)))
        elif "attention_stale" in warning_flags or "gyro_stale" in warning_flags:
            quality_state = "warning"
            signal_reliable = False
            estimation_allowed = False
            reasons.extend([x for x in ("attention_stale", "gyro_stale") if x in warning_flags])
        elif "attention_missing" in warning_flags or "gyro_missing" in warning_flags:
            quality_state = "warning"
            signal_reliable = False
            estimation_allowed = False
            formal_training_allowed = False
            reasons.extend([x for x in ("attention_missing", "gyro_missing") if x in warning_flags])

        blocking_flags = {"attention_lost", "gyro_lost", "attention_missing", "gyro_missing", "attention_stale", "gyro_stale"}
        if calibration_usable and runtime_snapshot.get("attention_fresh") and runtime_snapshot.get("gyro_fresh") and not blocking_flags.intersection(set(warning_flags) | set(error_flags)):
            signal_reliable = True
            estimation_allowed = True

        if any(x in reasons for x in ("no_user", "no_profile", "no_calibration", "calibration_binding_inconsistent", "calibration_invalid")):
            quality_state = "error"
            calibration_usable = False
            formal_training_allowed = False
            estimation_allowed = False
        elif "low_baseline_confidence" in reasons and quality_state == "ok":
            quality_state = "warning"

        if quality_state == "error":
            sqi = 0.3
        elif quality_state == "warning":
            sqi = min(sqi, 0.74)
        return {
            "sqi": sqi,
            "quality_state": quality_state,
            "quality_reasons": sorted(set(reasons)),
            "q_attention": q_attention,
            "q_gyro": q_gyro,
            "q_motion": q_motion,
            "q_stream": q_stream,
            "calibration_usable": calibration_usable,
            "formal_training_allowed": formal_training_allowed,
            "signal_reliable": signal_reliable,
            "estimation_allowed": estimation_allowed,
        }
