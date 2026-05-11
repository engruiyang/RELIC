from __future__ import annotations

from datetime import datetime, timezone


class UserManager:
    def __init__(self, store):
        self.store = store
        self.current_user: dict | None = None

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def has_user(self) -> bool:
        return self.current_user is not None

    def list_users(self) -> list[dict]:
        return self.store.list_users()

    def create_local_user(self, user_id: str, display_name: str, user_type: str = "local_user") -> dict:
        now = self._now_iso()
        user = {
            "user_id": user_id,
            "display_name": display_name,
            "user_type": user_type,
            "created_at": now,
            "last_login_at": now,
        }
        self.store.upsert_user(user)
        self.current_user = user
        return user

    def create_local_user_if_absent(self, user_id: str, display_name: str) -> tuple[dict, bool]:
        existing = self.store.get_user(user_id)
        if existing is not None:
            self.current_user = existing
            return existing, False
        return self.create_local_user(user_id=user_id, display_name=display_name, user_type="local_user"), True

    def load_user(self, user_id: str) -> dict | None:
        user = self.store.get_user(user_id)
        if user is None:
            return None
        return self.select_current_user(user)

    def select_current_user(self, user: dict) -> dict:
        user = dict(user)
        user["last_login_at"] = self._now_iso()
        self.store.upsert_user(user)
        self.current_user = user
        return user

    def enter_guest_mode(self) -> dict:
        now = self._now_iso()
        user = {
            "user_id": "guest",
            "display_name": "Guest",
            "user_type": "guest",
            "created_at": now,
            "last_login_at": now,
        }
        self.current_user = user
        return user

    def ensure_demo_user(self) -> dict:
        demos = self.store.list_users_by_type("demo")
        if demos:
            return self.select_current_user(demos[0])
        return self.create_local_user(user_id="demo", display_name="Demo User", user_type="demo")
