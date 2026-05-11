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
        att.append({"attention": (0 if fail else 55 + (i % 5)), "attention_fresh": True, "error_flags": []})
    return gyro, att


def _load_user(mode: str, user_id: str | None, um: UserManager, pm: ProfileManager):
    if mode == "guest":
        return um.enter_guest_mode(), None
    if mode == "user":
        if not user_id:
            raise ValueError("--mode user requires --user-id")
        user = um.load_user(user_id)
        if user is None:
            raise ValueError(f"user not found: {user_id}")
        return user, pm.get_profile(user["user_id"])
    user = um.ensure_demo_user()
    return user, pm.get_profile(user["user_id"])


def run_calibration_action(action: str, mode: str, db_path: str, user_id: str | None = None, calibration_type: str = "auto", calibration_id: str | None = None, fail: bool = False) -> dict:
    storage = StorageManager(sqlite_path=db_path)
    storage.initialize()
    sm = StateMachine()
    sm.transition(SystemState.NO_USER)
    um, pm = UserManager(storage.sqlite), ProfileManager(storage.sqlite)
    cm = CalibrationManager(store=storage, profile_manager=pm)

    user, profile = _load_user(mode, user_id, um, pm)
    sm.transition(SystemState.USER_READY)

    out = {"db_path": db_path, "current_user_id": user["user_id"], "user_type": user["user_type"]}

    if action == "status":
        out |= cm.get_calibration_status(user["user_id"])
    elif action == "start":
        sm.transition(SystemState.CALIBRATING)
        gyro, att = _build_samples(fail=fail)
        cp = cm.start_calibration(user, calibration_type, gyro, att)
        sm.transition(SystemState.READY if cp.valid else SystemState.CALIBRATION_FAILED)
        out |= cp.to_dict()
        out["persisted"] = (user["user_type"] != "guest")
        out["profile.last_calibration_id"] = None if user["user_type"] == "guest" else pm.get_profile(user["user_id"])["last_calibration_id"]
    elif action == "cancel":
        sm.transition(SystemState.CALIBRATING)
        cp = cm.cancel_calibration(user)
        sm.transition(SystemState.CALIBRATION_FAILED)
        out |= cp.to_dict()
        out["persisted"] = False
        out["profile.last_calibration_id"] = None if user["user_type"] == "guest" else pm.get_profile(user["user_id"])["last_calibration_id"]
    elif action == "list":
        items = [] if user["user_type"] == "guest" else cm.list_calibrations(user["user_id"])
        bound = None if profile is None else profile.get("last_calibration_id")
        out["calibration_count"] = len(items)
        out["calibrations"] = [{"calibration_id": i["calibration_id"], "calibration_type": i["calibration_type"], "created_at": i["created_at"], "valid": bool(i["valid"]), "failure_reason": i["failure_reason"], "is_bound_to_profile": i["calibration_id"] == bound} for i in items]
    elif action == "latest":
        latest = None if user["user_type"] == "guest" else cm.get_latest_calibration(user["user_id"])
        out |= ({"latest": None} if latest is None else latest)
    elif action == "show":
        if not calibration_id:
            raise ValueError("--calibration-id is required")
        cp = cm.get_calibration(calibration_id)
        if cp is None:
            raise ValueError("calibration_not_found")
        out |= cp
    elif action == "bind":
        if user["user_type"] == "guest":
            raise ValueError("guest_bind_not_allowed")
        if not calibration_id:
            raise ValueError("--calibration-id is required")
        old, new = cm.bind_calibration_to_profile(user["user_id"], calibration_id)
        out["old_last_calibration_id"] = old
        out["new_last_calibration_id"] = new
    else:
        raise ValueError(f"unknown action: {action}")

    out["system_state"] = sm.state.value
    for k, v in out.items():
        print(f"{k}={v}")
    storage.shutdown()
    return out


def run_calibration(mode: str, db_path: str, user_id: str | None = None, fail: bool = False) -> dict:
    return run_calibration_action("start", mode, db_path, user_id=user_id, calibration_type="auto", fail=fail)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--action", choices=["status", "start", "cancel", "list", "latest", "show", "bind"], default="start")
    p.add_argument("--mode", choices=["demo", "user", "guest"], default="demo")
    p.add_argument("--user-id")
    p.add_argument("--db-path", default="data/relic_local.db")
    p.add_argument("--calibration-type", choices=["auto", "first_profile", "quick_check", "periodic", "triggered"], default="auto")
    p.add_argument("--calibration-id")
    p.add_argument("--fail", action="store_true")
    args = p.parse_args()
    run_calibration_action(args.action, args.mode, args.db_path, args.user_id, args.calibration_type, args.calibration_id, args.fail)


if __name__ == "__main__":
    main()
