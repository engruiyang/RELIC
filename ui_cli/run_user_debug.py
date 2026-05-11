from __future__ import annotations

import argparse

from core.state_machine import StateMachine, SystemState
from storage.storage_manager import StorageManager
from user.profile_manager import ProfileManager
from user.user_manager import UserManager


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["demo", "guest"], default="demo")
    p.add_argument("--db-path", default="data/relic_local.db")
    return p


def run_user_debug(mode: str = "demo", db_path: str = "data/relic_local.db") -> dict:
    storage = StorageManager(sqlite_path=db_path)
    storage.initialize()
    sm = StateMachine()
    sm.transition(SystemState.NO_USER)

    user_manager = UserManager(storage.sqlite)
    profile_manager = ProfileManager(storage.sqlite)

    profile = None
    persisted = False
    if mode == "guest":
        user = user_manager.enter_guest_mode()
    else:
        user = user_manager.ensure_demo_user()
        profile = profile_manager.load_profile(user["user_id"])
        persisted = True

    sm.transition(SystemState.USER_READY)
    output = {
        "db_path": db_path,
        "current_user_id": user["user_id"],
        "display_name": user["display_name"],
        "user_type": user["user_type"],
        "last_login_at": user["last_login_at"],
        "persisted": persisted,
        "profile_loaded": profile is not None,
        "system_state": sm.state.value,
    }
    if profile is not None:
        output.update(
            {
                "profile.attention_low_threshold": profile["attention_low_threshold"],
                "profile.attention_high_threshold": profile["attention_high_threshold"],
                "profile.preferred_game_id": profile["preferred_game_id"],
                "profile.difficulty_level": profile["difficulty_level"],
                "profile.last_calibration_id": profile["last_calibration_id"],
            }
        )

    for k, v in output.items():
        print(f"{k}={v}")

    storage.shutdown()
    return output


def main() -> None:
    args = build_parser().parse_args()
    run_user_debug(mode=args.mode, db_path=args.db_path)


if __name__ == "__main__":
    main()
