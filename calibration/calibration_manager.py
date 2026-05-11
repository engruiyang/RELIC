from __future__ import annotations

import math
import time
import uuid
from datetime import datetime, timezone
from statistics import median
from typing import Callable

from calibration.calibration_profile import CalibrationProfile

PHASE_PROMPTS = {
    "preparation": {
        "title": "佩戴检查",
        "user_instruction": "请确认头环贴合额头，头部坐正，眼睛自然看向屏幕。",
        "avoid_instruction": "避免头发夹在电极和皮肤之间，不要移动头环。",
        "duration_hint": "约 2 秒",
    },
    "gyro_static_baseline": {
        "title": "静止姿态校准",
        "user_instruction": "请保持头部静止，眼睛自然平视屏幕中央。",
        "avoid_instruction": "不要转头、低头、抬头或晃动身体。",
        "duration_hint": "约 3 秒",
    },
    "attention_quick_baseline": {
        "title": "注意力基线检查",
        "user_instruction": "请自然平视屏幕中央，保持清醒和安静。",
        "avoid_instruction": "不要说话、不要刻意用力集中、不要大幅移动头部。",
        "duration_hint": "约 8 到 12 秒",
    },
    "result": {
        "title": "结果计算",
        "user_instruction": "正在生成校准结果，请稍候。",
        "avoid_instruction": "无需操作。",
        "duration_hint": "约 1 秒",
    },
}

RECOVERY_HINTS = {
    "attention_missing": "未检测到稳定注意力数据。请检查头环佩戴、电极接触和平台连接。",
    "attention_lost": "注意力数据中断。请保持静止并检查平台连接后重试。",
    "attention_zero_stuck": "注意力值长期为0。请调整佩戴并确认设备连接正常。",
    "attention_valid_ratio_low": "注意力有效样本比例过低。请保持安静并重试。",
    "gyro_missing": "未检测到陀螺仪数据。请检查设备连接状态。",
    "gyro_lost": "陀螺仪数据中断。请检查连接并保持头部稳定。",
    "gyro_unstable": "校准期间头部移动过大。请保持头部静止后重试。",
    "stream_inactive": "数据流未激活。请确认平台已开始推流。",
    "insufficient_valid_samples": "有效样本不足。请稳定佩戴并重试一次。",
    "cancelled_by_user": "您已取消本次校准。准备好后可重新开始。",
}


class CalibrationManager:
    def __init__(self, store=None, profile_manager=None, min_valid_ratio: float = 0.7, gyro_noise_rms_threshold: float = 1.2, attention_shift_threshold: float = 30.0):
        self.store = store
        self.profile_manager = profile_manager
        self.min_valid_ratio = min_valid_ratio
        self.gyro_noise_rms_threshold = gyro_noise_rms_threshold
        self.attention_shift_threshold = attention_shift_threshold

    def get_recovery_hint(self, failure_reason: str | None) -> str | None:
        if not failure_reason:
            return None
        return RECOVERY_HINTS.get(failure_reason, "请检查佩戴、连接状态并重试。")

    def start_calibration(self, user: dict, calibration_type: str, gyro_snapshots: list[dict], attention_snapshots: list[dict], *, fast: bool = True, emit_event: Callable[[dict], None] | None = None, device_id: str = "mock_device") -> CalibrationProfile:
        if self.store is None:
            raise ValueError("store is required")
        history = self.list_calibrations(user["user_id"]) if user["user_type"] != "guest" else []
        resolved_type = "quick_check" if calibration_type == "auto" and bool(history) else ("first_profile" if calibration_type == "auto" else calibration_type)
        pending_id = f"pending_{uuid.uuid4().hex[:10]}"
        phase_names = ["preparation", "gyro_static_baseline", "attention_quick_baseline", "result"]
        phase_count = len(phase_names)
        phase_ms = 200 if fast else 2500
        t0 = time.monotonic()

        def emit(event_type: str, phase: str, phase_index: int, progress: float, message: str = ""):
            if emit_event is None:
                return
            prompt = PHASE_PROMPTS.get(phase, {})
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            emit_event({
                "event_type": event_type,
                "pending_calibration_id": pending_id,
                "user_id": user["user_id"],
                "calibration_type": resolved_type,
                "phase": phase,
                "phase_index": phase_index,
                "phase_count": phase_count,
                "progress": progress,
                "elapsed_ms": elapsed_ms,
                "remaining_ms": max(0, phase_ms * phase_count - elapsed_ms),
                "message": message,
                "cancellable": True,
                "title": prompt.get("title", phase),
                "user_instruction": prompt.get("user_instruction", ""),
                "avoid_instruction": prompt.get("avoid_instruction", ""),
                "duration_hint": prompt.get("duration_hint", ""),
            })

        emit("calibration_started", phase_names[0], 1, 0.0, "calibration started")
        for i, phase in enumerate(phase_names, start=1):
            emit("calibration_phase_started", phase, i, (i - 1) / phase_count, f"phase started: {phase}")
            steps = 1 if fast else 3
            for s in range(steps):
                if not fast:
                    time.sleep(phase_ms / steps / 1000.0)
                emit("calibration_progress", phase, i, min(0.99, ((i - 1) + (s + 1) / steps) / phase_count), f"phase progress: {phase}")
            emit("calibration_phase_completed", phase, i, i / phase_count, f"phase completed: {phase}")

        hist_base = history[-1].get("attention_baseline") if history else None
        cp = self.run_quick_calibration(user_id=user["user_id"], user_type=user["user_type"], device_id=device_id, gyro_snapshots=gyro_snapshots, attention_snapshots=attention_snapshots, has_history=(resolved_type == "quick_check"), historical_baseline=hist_base)
        cp.calibration_type = resolved_type
        final_stats = {
            "collected_samples": len(gyro_snapshots) + len(attention_snapshots),
            "valid_attention_samples": sum(1 for x in attention_snapshots if x.get("attention_fresh") and not x.get("error_flags") and x.get("attention") is not None),
            "valid_gyro_samples": sum(1 for x in gyro_snapshots if x.get("gyro_fresh") and not x.get("error_flags") and x.get("gyro_x") is not None),
            "attention_valid_sample_ratio": cp.attention_valid_sample_ratio,
            "valid": cp.valid,
            "failure_reason": cp.failure_reason,
            "user_recovery_hint": self.get_recovery_hint(cp.failure_reason),
        }
        if cp.valid:
            emit("calibration_completed", "result", phase_count, 1.0, "calibration completed")
            if emit_event is not None:
                emit_event(final_stats | {"event_type": "calibration_completed_summary", "user_id": user["user_id"], "calibration_type": resolved_type, "phase": "result", "phase_index": phase_count, "phase_count": phase_count, "progress": 1.0, "elapsed_ms": int((time.monotonic() - t0) * 1000), "remaining_ms": 0, "cancellable": False, "title": PHASE_PROMPTS["result"]["title"], "user_instruction": PHASE_PROMPTS["result"]["user_instruction"], "avoid_instruction": PHASE_PROMPTS["result"]["avoid_instruction"], "duration_hint": PHASE_PROMPTS["result"]["duration_hint"], "message": "final summary"})
        else:
            emit("calibration_failed", "result", phase_count, 1.0, cp.failure_reason or "calibration failed")
            if emit_event is not None:
                emit_event(final_stats | {"event_type": "calibration_failed_summary", "user_id": user["user_id"], "calibration_type": resolved_type, "phase": "result", "phase_index": phase_count, "phase_count": phase_count, "progress": 1.0, "elapsed_ms": int((time.monotonic() - t0) * 1000), "remaining_ms": 0, "cancellable": False, "title": PHASE_PROMPTS["result"]["title"], "user_instruction": PHASE_PROMPTS["result"]["user_instruction"], "avoid_instruction": PHASE_PROMPTS["result"]["avoid_instruction"], "duration_hint": PHASE_PROMPTS["result"]["duration_hint"], "message": "final summary"})

        if user["user_type"] != "guest":
            self.store.save_calibration_profile(cp.to_dict())
            if cp.valid and self.profile_manager is not None:
                self.profile_manager.update_last_calibration_id(user["user_id"], cp.calibration_id)
        return cp

    def cancel_calibration(self, user: dict, reason: str = "cancelled_by_user") -> CalibrationProfile:
        return CalibrationProfile(calibration_id=f"cal_{uuid.uuid4().hex[:12]}", user_id=user["user_id"], device_id="mock_device", created_at=datetime.now(timezone.utc).isoformat(), calibration_type="triggered", attention_baseline=None, attention_std=None, attention_valid_sample_ratio=0.0, gyro_bias_x=None, gyro_bias_y=None, gyro_bias_z=None, gyro_noise_x=None, gyro_noise_y=None, gyro_noise_z=None, gyro_noise_rms=None, gyro_stability_score=0.0, signal_quality_baseline=0.0, valid=False, failure_reason=reason, non_persistent=True)

    def get_latest_calibration(self, user_id: str) -> dict | None: return None if self.store is None else self.store.get_latest_calibration_profile(user_id)
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
        bound = self.get_calibration(bound_id) if bound_id else None
        bound_exists = bound is not None
        bound_valid = bool(bound["valid"]) if bound else False
        bound_user_ok = (bound.get("user_id") == user_id) if bound else False
        bound_source = None if not bound else ("mock" if bound.get("device_id") == "mock_device" else "ipc")
        consistent = bool(bound_id and bound_exists and bound_valid and bound_user_ok)
        hint = None if consistent else "检测到历史绑定不一致。请使用 bind 重新绑定有效校准。"
        return {
            "profile_loaded": profile is not None,
            "profile.last_calibration_id": bound_id,
            "bound_calibration_exists": bound_exists,
            "bound_calibration_valid": bound_valid,
            "bound_calibration_user_matches": bound_user_ok,
            "bound_calibration_source": bound_source,
            "binding_consistent": consistent,
            "latest_calibration_id": None if latest is None else latest["calibration_id"],
            "latest_calibration_type": None if latest is None else latest["calibration_type"],
            "latest_valid": None if latest is None else bool(latest["valid"]),
            "user_recovery_hint": hint,
        }

    def run_quick_calibration(self, *, user_id: str, user_type: str, device_id: str, gyro_snapshots: list[dict], attention_snapshots: list[dict], has_history: bool, historical_baseline: float | None) -> CalibrationProfile:
        valid, failure_reason, metrics = self._compute_metrics(gyro_snapshots, attention_snapshots, historical_baseline)
        return CalibrationProfile(calibration_id=f"cal_{uuid.uuid4().hex[:12]}", user_id=user_id, device_id=device_id, created_at=datetime.now(timezone.utc).isoformat(), calibration_type=("quick_check" if has_history else "first_profile"), attention_baseline=metrics["attention_baseline"], attention_std=metrics["attention_std"], attention_valid_sample_ratio=metrics["attention_valid_sample_ratio"], gyro_bias_x=metrics["gyro_bias_x"], gyro_bias_y=metrics["gyro_bias_y"], gyro_bias_z=metrics["gyro_bias_z"], gyro_noise_x=metrics["gyro_noise_x"], gyro_noise_y=metrics["gyro_noise_y"], gyro_noise_z=metrics["gyro_noise_z"], gyro_noise_rms=metrics["gyro_noise_rms"], gyro_stability_score=metrics["gyro_stability_score"], signal_quality_baseline=metrics["signal_quality_baseline"], valid=valid, failure_reason=failure_reason, non_persistent=(user_type == "guest"))

    def _compute_metrics(self, gyro_snapshots: list[dict], attention_snapshots: list[dict], historical_baseline: float | None):
        def mad(values: list[float], med: float) -> float: return 1.4826 * median([abs(v - med) for v in values])
        valid_gyro = [s for s in gyro_snapshots if s.get("gyro_fresh") and not s.get("error_flags") and s.get("gyro_x") is not None]
        gr = len(valid_gyro) / max(len(gyro_snapshots), 1)
        if gr < self.min_valid_ratio: return False, "insufficient_valid_samples", self._empty_metrics(gr, 0.0)
        gx, gy, gz = [float(s["gyro_x"]) for s in valid_gyro], [float(s["gyro_y"]) for s in valid_gyro], [float(s["gyro_z"]) for s in valid_gyro]
        bx, by, bz = median(gx), median(gy), median(gz)
        nx, ny, nz = mad(gx, bx), mad(gy, by), mad(gz, bz)
        nrms = math.sqrt((nx * nx + ny * ny + nz * nz) / 3.0)
        if nrms > self.gyro_noise_rms_threshold: return False, "gyro_unstable", self._empty_metrics(gr, 0.0) | {"gyro_bias_x": bx, "gyro_bias_y": by, "gyro_bias_z": bz, "gyro_noise_x": nx, "gyro_noise_y": ny, "gyro_noise_z": nz, "gyro_noise_rms": nrms, "gyro_stability_score": max(0.0, 1.0 - nrms / self.gyro_noise_rms_threshold)}
        valid_att = [s for s in attention_snapshots if s.get("attention_fresh") and not s.get("error_flags") and s.get("attention") is not None]
        ar = len(valid_att) / max(len(attention_snapshots), 1)
        if ar < self.min_valid_ratio: return False, "insufficient_valid_samples", self._empty_metrics(gr, ar)
        av = [float(s["attention"]) for s in valid_att]
        if not av or all(v == 0 for v in av): return False, "attention_lost", self._empty_metrics(gr, ar)
        abaseline, astd = median(av), mad(av, median(av))
        if historical_baseline is not None and abs(abaseline - historical_baseline) > self.attention_shift_threshold: return False, "attention_baseline_shift", self._empty_metrics(gr, ar) | {"attention_baseline": abaseline, "attention_std": astd}
        return True, None, {"attention_baseline": abaseline, "attention_std": astd, "attention_valid_sample_ratio": ar, "gyro_bias_x": bx, "gyro_bias_y": by, "gyro_bias_z": bz, "gyro_noise_x": nx, "gyro_noise_y": ny, "gyro_noise_z": nz, "gyro_noise_rms": nrms, "gyro_stability_score": max(0.0, 1.0 - nrms / self.gyro_noise_rms_threshold), "signal_quality_baseline": min(gr, ar)}

    def _empty_metrics(self, gr: float, ar: float) -> dict:
        return {"attention_baseline": None, "attention_std": None, "attention_valid_sample_ratio": ar, "gyro_bias_x": None, "gyro_bias_y": None, "gyro_bias_z": None, "gyro_noise_x": None, "gyro_noise_y": None, "gyro_noise_z": None, "gyro_noise_rms": None, "gyro_stability_score": 0.0, "signal_quality_baseline": min(gr, ar)}
