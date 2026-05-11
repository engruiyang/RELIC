from __future__ import annotations

from datetime import datetime, timezone


class ProfileManager:
    def __init__(self, store):
        self.store = store

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _default_profile(self, user_id: str) -> dict:
        return {
            "user_id": user_id,
            "attention_low_threshold": 40,
            "attention_high_threshold": 70,
            "preferred_game_id": "",
            "difficulty_level": 1,
            "last_calibration_id": None,
            "updated_at": self._now_iso(),
        }

    def load_profile(self, user_id: str) -> dict:
        profile = self.store.get_user_profile(user_id)
        if profile is not None:
            return profile
        profile = self._default_profile(user_id)
        self.store.upsert_user_profile(profile)
        return profile

    def save_profile(self, profile: dict) -> dict:
        payload = dict(profile)
        payload["updated_at"] = self._now_iso()
        self.store.upsert_user_profile(payload)
        return payload


    def update_last_calibration_id(self, user_id: str, calibration_id: str) -> dict:
        profile = self.load_profile(user_id)
        profile["last_calibration_id"] = calibration_id
        return self.save_profile(profile)
