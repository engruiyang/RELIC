from __future__ import annotations

import argparse

from calibration.calibration_manager import CalibrationManager
from core.state_machine import StateMachine, SystemState
from storage.storage_manager import StorageManager
from user.profile_manager import ProfileManager
from user.user_manager import UserManager


def _build_samples(fail: bool = False) -> tuple[list[dict], list[dict]]:
    gyro, att = [], []
    for i in range(60):
        gyro.append({"gyro_x": 0.01 * (i % 3), "gyro_y": -0.01 * (i % 2), "gyro_z": 0.02, "gyro_fresh": True, "error_flags": []})
    for i in range(120):
        v = 55 + (i % 5)
        att.append({"attention": 0 if fail else v, "attention_fresh": True, "error_flags": []})
    return gyro, att


def run_calibration(mode: str, db_path: str, user_id: str | None = None, fail: bool = False) -> dict:
    storage = StorageManager(sqlite_path=db_path)
    storage.initialize()
    sm = StateMachine()
    sm.transition(SystemState.NO_USER)
    um, pm = UserManager(storage.sqlite), ProfileManager(storage.sqlite)

    if mode == "guest":
        user = um.enter_guest_mode()
        persisted = False
        profile = None
    elif mode == "user":
        if not user_id:
            raise ValueError("--mode user requires --user-id")
        user = um.load_user(user_id)
        if user is None:
            raise ValueError(f"user not found: {user_id}")
        profile = pm.load_profile(user["user_id"])
        persisted = True
    else:
        user = um.ensure_demo_user()
        profile = pm.load_profile(user["user_id"])
        persisted = True

    sm.transition(SystemState.USER_READY)
    sm.transition(SystemState.CALIBRATING)
    history = storage.list_calibration_profiles(user["user_id"]) if persisted else []
    hist_base = history[-1]["attention_baseline"] if history else None

    gyro, att = _build_samples(fail=fail)
    cp = CalibrationManager().run_quick_calibration(
        user_id=user["user_id"], user_type=user["user_type"], device_id="mock_device", gyro_snapshots=gyro, attention_snapshots=att, has_history=bool(history), historical_baseline=hist_base
    )

    if cp.valid:
        sm.transition(SystemState.READY)
        if persisted and not cp.non_persistent:
            storage.save_calibration_profile(cp.to_dict())
            profile = pm.update_last_calibration_id(user["user_id"], cp.calibration_id)
    else:
        sm.transition(SystemState.CALIBRATION_FAILED)

    out = {
        "db_path": db_path,
        "current_user_id": user["user_id"],
        "user_type": user["user_type"],
        "calibration_id": cp.calibration_id,
        "calibration_type": cp.calibration_type,
        "valid": cp.valid,
        "failure_reason": cp.failure_reason,
        "attention_baseline": cp.attention_baseline,
        "attention_std": cp.attention_std,
        "attention_valid_sample_ratio": cp.attention_valid_sample_ratio,
        "gyro_bias_x": cp.gyro_bias_x,
        "gyro_bias_y": cp.gyro_bias_y,
        "gyro_bias_z": cp.gyro_bias_z,
        "gyro_noise_rms": cp.gyro_noise_rms,
        "gyro_stability_score": cp.gyro_stability_score,
        "profile.last_calibration_id": None if profile is None else profile["last_calibration_id"],
        "system_state": sm.state.value,
        "persisted": persisted and cp.valid and not cp.non_persistent,
    }
    for k, v in out.items():
        print(f"{k}={v}")
    storage.shutdown()
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["demo", "user", "guest"], default="demo")
    p.add_argument("--user-id")
    p.add_argument("--db-path", default="data/relic_local.db")
    p.add_argument("--fail", action="store_true")
    args = p.parse_args()
    run_calibration(args.mode, args.db_path, args.user_id, args.fail)


if __name__ == "__main__":
    main()
