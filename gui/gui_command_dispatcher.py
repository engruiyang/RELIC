from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from storage.replay_adapter import ReplayAdapter
from storage.session_report_writer import write_session_report
from storage.sqlite_store import SqliteStore
from ui_cli.run_game_debug import run_game_debug_session


@dataclass(slots=True)
class CommandResult:
    command: str
    accepted: bool
    status: str
    message: str
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class GuiCommandDispatcher:
    def __init__(self, source: Any) -> None:
        self._source = source

    def dispatch(self, command: str, args: dict[str, Any]) -> CommandResult:
        handler = getattr(self, f"_cmd_{command}", None)
        if handler is None:
            return CommandResult(command, False, "rejected", "unsupported_command", {})
        try:
            return handler(args)
        except Exception as exc:
            return CommandResult(command, False, "failed", str(exc), {})

    def _cmd_load_demo_user(self, args: dict[str, Any]) -> CommandResult:
        _ = args
        self._source.load_demo_user()
        return CommandResult("load_demo_user", True, "accepted", "demo_user_loaded", {"user_id": "demo_user"})

    def _cmd_refresh_snapshot(self, args: dict[str, Any]) -> CommandResult:
        _ = args
        self._source.refresh_snapshot()
        return CommandResult("refresh_snapshot", True, "accepted", "snapshot_refreshed", {})

    def _cmd_start_mock_session(self, args: dict[str, Any]) -> CommandResult:
        duration_sec = int(args.get("duration_sec", self._source.duration_sec))
        result = run_game_debug_session(
            db_path=self._source.db_path,
            duration_sec=duration_sec,
            user_id=str(args.get("user_id", self._source.user_id)),
            game_id=str(args.get("game_id", self._source.game_id)),
            task6b_config=str(args.get("task6b_config", self._source.task6b_config)),
        )
        replay = ReplayAdapter()
        replay_stats = replay.replay(result["log_path"], speed=0)
        out = dict(result)
        out["report_path"] = write_session_report(out, replay_stats, report_error=None)
        self._source.apply_session_summary(out)
        return CommandResult("start_mock_session", True, "completed", "mock session completed", out)

    def _cmd_end_session(self, args: dict[str, Any]) -> CommandResult:
        _ = args
        return CommandResult("end_session", True, "noop", "no_active_session", {})

    def _cmd_open_last_report(self, args: dict[str, Any]) -> CommandResult:
        _ = args
        report_path = str(self._source.get_session_state().get("report_path") or "")
        if not report_path:
            return CommandResult("open_last_report", False, "failed", "report_path_missing", {})
        return CommandResult("open_last_report", True, "accepted", "report_path_ready", {"report_path": report_path})
