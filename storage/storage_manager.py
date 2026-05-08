from storage.jsonl_logger import JsonlLogger
from storage.sqlite_store import SqliteStore
class StorageManager:
    def __init__(self): self.jsonl=JsonlLogger(); self.sqlite=SqliteStore()
