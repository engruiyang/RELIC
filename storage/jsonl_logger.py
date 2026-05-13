from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


class JsonlLogger:
    def __init__(self) -> None:
        self._fp = None
        self._path: str | None = None

    def open(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._fp = open(path, "a", encoding="utf-8")
        self._path = path

    def write_event(self, event_type: str, session_id: str, payload: dict[str, Any]) -> None:
        if self._fp is None:
            raise RuntimeError("JsonlLogger is not opened")
        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "session_id": session_id,
            "payload": payload,
        }
        json.dumps(row)
        self._fp.write(json.dumps(row, ensure_ascii=False) + "\n")
        self._fp.flush()

    def close(self) -> None:
        if self._fp is not None:
            self._fp.flush()
            self._fp.close()
            self._fp = None

    @property
    def path(self) -> str | None:
        return self._path
