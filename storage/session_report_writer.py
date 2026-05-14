from __future__ import annotations

from pathlib import Path
from typing import Any


def write_session_report(session_summary: dict[str, Any], replay_summary: dict[str, Any], report_error: str | None = None, out_dir: str = "reports/sessions") -> str:
    session_id = session_summary.get("session_id", "unknown_session")
    p = Path(out_dir) / f"{session_id}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    text = f"""# RELIC 训练会话报告

- session_id: {session_summary.get('session_id')}
- user_id: {session_summary.get('user_id')}
- game_id: {session_summary.get('game_id')}
- log_path: {session_summary.get('log_path')}
- score: {session_summary.get('score')}
- fi_avg: {session_summary.get('fi_avg')}
- sqi_avg: {session_summary.get('sqi_avg')}
- warning_count: {session_summary.get('warning_count')}
- error_count: {session_summary.get('error_count')}
- platform_report_status: {session_summary.get('platform_report_status')}
- platform_report_error: {report_error}
- replay_event_count: {replay_summary.get('event_count')}

训练摘要来源：SQLite summary + JSONL replay summary

备注：当前报告由 headless mock/e2e 流程生成，真实平台联调状态另行记录。
"""
    p.write_text(text, encoding="utf-8")
    return p.as_posix()
