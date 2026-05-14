from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PlatformReportResult:
    session_id: str
    status: str
    error: str | None = None
    raw: dict[str, Any] | None = None


class InMemoryPlatformSender:
    def __init__(self) -> None:
        self.messages: list[dict[str, Any]] = []

    def send(self, msg: dict[str, Any]) -> None:
        self.messages.append(msg)


class PlatformReporter:
    def __init__(self, sender: InMemoryPlatformSender | None = None) -> None:
        self.sender = sender or InMemoryPlatformSender()
        self._results: dict[str, PlatformReportResult] = {}

    def build_mouse_list(self, game_manifest: dict[str, Any]) -> dict[str, Any]:
        actions = game_manifest.get("supported_event_types") or []
        return {"type": "ipc_mouse_list", "actions": list(actions)}

    def build_test_start(self, session: dict[str, Any]) -> dict[str, Any]:
        return {"type": "ipc_test_start", "session_id": session.get("session_id"), "user_id": session.get("user_id"), "game_id": session.get("game_id")}

    def build_test_stop(self, session_summary: dict[str, Any]) -> dict[str, Any]:
        return {"type": "ipc_test_stop", "session_id": session_summary.get("session_id"), "score": session_summary.get("score"), "status": session_summary.get("status")}

    def map_game_event_to_mouse_data(self, game_event: dict[str, Any]) -> dict[str, Any] | None:
        if game_event.get("event_type") not in {"user_action", "target_click"}:
            return None
        payload = game_event.get("payload") or {}
        return {"type": "ipc_mouse_data", "session_id": game_event.get("session_id"), "index": payload.get("index", payload.get("target_index", 0)), "timestamp_ms": game_event.get("created_at_ms")}

    def handle_algorithm_stop_test(self, message: dict[str, Any]) -> PlatformReportResult:
        sid = message.get("session_id")
        ok = bool(message.get("uploaded", False))
        r = PlatformReportResult(session_id=sid, status=("uploaded" if ok else "failed"), error=message.get("error_reason"), raw=message)
        self._results[sid] = r
        return r

    def record_report_result(self, session_id: str, result: PlatformReportResult) -> None:
        self._results[session_id] = result

    def get_report_result(self, session_id: str) -> PlatformReportResult | None:
        return self._results.get(session_id)

    def send(self, msg: dict[str, Any]) -> None:
        self.sender.send(msg)
