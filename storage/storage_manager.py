from storage.jsonl_logger import JsonlLogger
from storage.sqlite_store import SqliteStore


class StorageManager:
    def __init__(self, sqlite_path: str = "data/relic_local.db"):
        self.jsonl = JsonlLogger()
        self.sqlite = SqliteStore(db_path=sqlite_path)

    def initialize(self) -> None:
        self.sqlite.connect()

    def shutdown(self) -> None:
        self.sqlite.close()

    def save_calibration_profile(self, profile: dict) -> None:
        self.sqlite.insert_calibration_profile(profile)

    def list_calibration_profiles(self, user_id: str) -> list[dict]:
        return self.sqlite.list_calibration_profiles(user_id)

    def get_calibration_profile(self, calibration_id: str) -> dict | None:
        return self.sqlite.get_calibration_profile(calibration_id)

    def get_latest_calibration_profile(self, user_id: str) -> dict | None:
        return self.sqlite.get_latest_calibration_profile(user_id)
