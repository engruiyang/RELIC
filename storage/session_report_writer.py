from __future__ import annotations

from pathlib import Path
from typing import Any
import json


def extract_session_summary_from_jsonl(log_path: str) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if not log_path:
        return payload
    p = Path(log_path)
    if not p.exists():
        return payload
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("event_type") == "session_summary" and isinstance(row.get("payload"), dict):
            payload = dict(row["payload"])
    return payload


def merge_non_null(primary: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
    merged = dict(secondary)
    for k, v in primary.items():
        if v is None:
            continue
        if isinstance(v, str) and v == "":
            continue
        merged[k] = v
    return merged


def write_session_report(session_summary: dict[str, Any], replay_summary: dict[str, Any], report_error: str | None = None, out_dir: str = "reports/sessions") -> str:
    jsonl_summary = extract_session_summary_from_jsonl(str(session_summary.get("log_path") or ""))
    merged = merge_non_null(jsonl_summary, session_summary)
    session_id = merged.get("session_id", "unknown_session")
    fi_avg = merged.get("fi_avg")
    if fi_avg is None:
        fi_avg = merged.get("final_fi_avg")
    sqi_avg = merged.get("sqi_avg")
    if sqi_avg is None:
        sqi_avg = merged.get("final_sqi_avg")
    platform_status = merged.get("platform_report_status") or "not_applicable"
    platform_error = report_error if report_error not in (None, "") else (merged.get("platform_report_error") or "none")
    session_type = str(merged.get("session_type") or "").strip().lower()
    is_training = session_type == "training"

    def val(name: str, default: str = "unknown") -> Any:
        x = merged.get(name)
        return default if x is None else x

    p = Path(out_dir) / f"{session_id}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    if is_training:
        lines = [
            "# RELIC Link Diagnostics",
            "",
            f"- session_id: {val('session_id')}",
            f"- session_type: {val('session_type')}",
            f"- user_id: {val('user_id')}",
            f"- game_id: {val('game_id')}",
            "- protocol_name: TraceLock Protocol",
            f"- log_path: {val('log_path')}",
            f"- Trace Score: {val('score')}",
            f"- Sync Chain / max_combo: {val('combo')}/{val('max_combo')}",
            f"- Trace Retention / accuracy: {val('accuracy')}",
            f"- Trace Drop / omission: {val('omission')}",
            f"- False Action: {val('false_action')}",
            f"- RT Stability: {val('rt_stability')}",
            f"- fi_avg: {fi_avg if fi_avg is not None else 'unknown'}",
            f"- sqi_avg: {sqi_avg if sqi_avg is not None else 'unknown'}",
            f"- valid_duration_ms: {val('valid_duration_ms')}",
            f"- warning_duration_ms: {val('warning_duration_ms')}",
            f"- error_count: {val('error_count')}",
            f"- total_duration_ms: {val('total_duration_ms')}",
            f"- control_state_summary: {val('control_state_summary')}",
            f"- quality_state_summary: {val('quality_state_summary')}",
            f"- calibration_status: {val('calibration_status')}",
            f"- profile_status: {val('profile_status')}",
            f"- game_event_count: {val('game_event_count')}",
            f"- score_update_count: {val('score_update_count')}",
            f"- behavior_sample_count: {val('behavior_sample_count')}",
            f"- training_window_count: {val('training_window_count')}",
            f"- fi_window_avg: {val('fi_window_avg')}",
            f"- fi_window_min: {val('fi_window_min')}",
            f"- fi_window_max: {val('fi_window_max')}",
            f"- perf_window_avg: {val('perf_window_avg')}",
            f"- sqi_window_avg: {val('sqi_window_avg')}",
            f"- low_sqi_window_count: {val('low_sqi_window_count')}",
            f"- stable_focus_window_count: {val('stable_focus_window_count')}",
            f"- high_focus_window_count: {val('high_focus_window_count')}",
            f"- stable_focus_total_ms: {val('stable_focus_total_ms')}",
            f"- difficulty_suggestion_summary: {val('difficulty_suggestion_summary')}",
            f"- feedback_mode_summary: {val('feedback_mode_summary')}",
            f"- conflict_hold_count: {val('conflict_hold_count')}",
            f"- signal_check_count: {val('signal_check_count')}",
            f"- behavior_window_source_summary: {val('behavior_window_source_summary')}",
            f"- carried_forward_window_count: {val('carried_forward_window_count')}",
            f"- session_final_behavior_window_count: {val('session_final_behavior_window_count')}",
            f"- window_snapshot_behavior_window_count: {val('window_snapshot_behavior_window_count')}",
            f"- insufficient_behavior_window_count: {val('insufficient_behavior_window_count')}",
            f"- platform_report_status: {platform_status}",
            f"- platform_report_error: {platform_error}",
            f"- replay_event_count: {replay_summary.get('event_count')}",
            "",
            "训练摘要来源：SQLite training summary + TraceLock behavior summary",
            "",
            "备注：当前报告由 live-control training session 生成，包含 TraceLock 行为指标与链路摘要。",
        ]
    else:
        lines = [
            "# RELIC 训练会话报告",
            "",
            f"- session_id: {val('session_id')}",
            f"- session_type: {val('session_type')}",
            f"- user_id: {val('user_id')}",
            f"- game_id: {val('game_id')}",
            f"- log_path: {val('log_path')}",
            f"- score: {val('score')}",
            f"- fi_avg: {fi_avg if fi_avg is not None else 'unknown'}",
            f"- sqi_avg: {sqi_avg if sqi_avg is not None else 'unknown'}",
            f"- valid_duration_ms: {val('valid_duration_ms')}",
            f"- warning_duration_ms: {val('warning_duration_ms')}",
            f"- error_count: {val('error_count')}",
            f"- total_duration_ms: {val('total_duration_ms')}",
            f"- control_state_summary: {val('control_state_summary')}",
            f"- quality_state_summary: {val('quality_state_summary')}",
            f"- game_event_count: {val('game_event_count')}",
            f"- score_update_count: {val('score_update_count')}",
            f"- behavior_sample_count: {val('behavior_sample_count')}",
            f"- platform_report_status: {platform_status}",
            f"- platform_report_error: {platform_error}",
            f"- replay_event_count: {replay_summary.get('event_count')}",
            "",
            "训练摘要来源：SQLite summary + JSONL replay summary",
            "",
            "备注：当前报告由 headless mock/e2e 流程生成，真实平台联调状态另行记录。",
        ]
    text = "\n".join(lines) + "\n"
    p.write_text(text, encoding="utf-8")
    return p.as_posix()
