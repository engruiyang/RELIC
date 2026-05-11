from __future__ import annotations

import argparse

from core.state_machine import StateMachine, SystemState
from storage.storage_manager import StorageManager
from user.profile_manager import ProfileManager
from user.user_manager import UserManager


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["demo", "guest", "user"], default="demo")
    p.add_argument("--user-id")
    p.add_argument("--display-name")
    p.add_argument("--list-users", action="store_true")
    p.add_argument("--create-user")
    p.add_argument("--db-path", default="data/relic_local.db")
    return p


def run_user_debug(mode: str = "demo", db_path: str = "data/relic_local.db", user_id: str | None = None) -> dict:
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
    elif mode == "user":
        if not user_id:
            raise ValueError("--mode user requires --user-id")
        loaded = user_manager.load_user(user_id)
        if loaded is None:
            raise ValueError(f"user not found: {user_id}")
        user = loaded
        profile = profile_manager.load_profile(user["user_id"])
        persisted = True
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
    storage = StorageManager(sqlite_path=args.db_path)
    storage.initialize()
    user_manager = UserManager(storage.sqlite)

    if args.list_users:
        print(f"db_path={args.db_path}")
        users = user_manager.list_users()
        print(f"user_count={len(users)}")
        for u in users:
            print(f"user_id={u['user_id']} display_name={u['display_name']} user_type={u['user_type']}")
        storage.shutdown()
        return

    if args.create_user:
        display_name = args.display_name or args.create_user
        user, created = user_manager.create_local_user_if_absent(args.create_user, display_name)
        print(f"db_path={args.db_path}")
        print(f"create_user_result={'created' if created else 'already_exists'}")
        print(f"current_user_id={user['user_id']}")
        storage.shutdown()
        return

    storage.shutdown()
    run_user_debug(mode=args.mode, db_path=args.db_path, user_id=args.user_id)


if __name__ == "__main__":
    main()
