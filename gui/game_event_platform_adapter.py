from __future__ import annotations

from typing import Any

from relic_platform.platform_reporter import InMemoryPlatformSender, PlatformReporter


class GameEventPlatformAdapter:
    def __init__(self, reporter: PlatformReporter | None = None, sender: InMemoryPlatformSender | None = None) -> None:
        self.sender = sender or InMemoryPlatformSender()
        self.reporter = reporter or PlatformReporter(sender=self.sender)
        self.platform_message_count = 0
        self.last_platform_message: dict[str, Any] = {}
        self.last_platform_result = "idle"

    def process_game_event(self, game_event: dict[str, Any], *, allow_mock: bool = True) -> dict[str, Any]:
        if not game_event.get("reportable", False):
            self.last_platform_result = "skipped_not_reportable"
            return {"platform_mocked": False, "reason": "not_reportable", "platform_result": self.last_platform_result}

        session_id = game_event.get("session_id")
        if not allow_mock or not session_id:
            self.last_platform_result = "game_event_recorded_no_session_context"
            print("[PLATFORM MOCK] skipped reason=no_session_context", flush=True)
            return {"platform_mocked": False, "reason": "no_session_context", "platform_result": self.last_platform_result}

        mapped_input = dict(game_event)
        if mapped_input.get("event_type") == "background_click":
            mapped_input["event_type"] = "target_click"
        mapped = self.reporter.map_game_event_to_mouse_data(mapped_input)
        if not mapped:
            self.last_platform_result = "skipped_unmapped_event_type"
            return {"platform_mocked": False, "reason": "unmapped_event_type", "platform_result": self.last_platform_result}
        payload = game_event.get("payload") or {}
        mapped["action_name"] = payload.get("action_name")
        self.reporter.send(mapped)
        self.platform_message_count = len(self.sender.messages)
        self.last_platform_message = dict(mapped)
        self.last_platform_result = "game_event_recorded_and_platform_mocked"
        print(
            f"[PLATFORM MOCK] type={mapped.get('type')} index={mapped.get('index')} action={mapped.get('action_name')} session_id={mapped.get('session_id')}",
            flush=True,
        )
        return {"platform_mocked": True, "reason": "mocked", "platform_result": self.last_platform_result, "platform_message": dict(mapped)}
