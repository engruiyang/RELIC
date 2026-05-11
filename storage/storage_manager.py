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
