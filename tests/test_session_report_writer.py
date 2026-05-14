import json
from pathlib import Path

from storage.session_report_writer import write_session_report


def test_write_session_report_prefers_jsonl_session_summary(tmp_path: Path) -> None:
    log_path = tmp_path / "session.jsonl"
    summary_payload = {
        "session_id": "s1",
        "user_id": "demo_user",
        "game_id": "fake_game",
        "score": 21.0,
        "final_fi_avg": 0.7,
        "final_sqi_avg": 0.9,
        "valid_duration_ms": 2000,
        "warning_duration_ms": 1000,
        "error_count": 0,
        "total_duration_ms": 3000,
        "control_state_summary": {"stable": 2},
        "quality_state_summary": {"good": 2},
        "game_event_count": 10,
        "score_update_count": 2,
        "behavior_sample_count": 3,
    }
    log_path.write_text(json.dumps({"event_type": "session_summary", "payload": summary_payload}) + "\n", encoding="utf-8")
    report_path = write_session_report(
        {"session_id": "s1", "user_id": None, "game_id": None, "fi_avg": None, "sqi_avg": None, "error_count": None, "log_path": str(log_path)},
        {"event_count": 5},
        report_error=None,
        out_dir=str(tmp_path / "reports"),
    )
    content = Path(report_path).read_text(encoding="utf-8")
    assert "user_id: demo_user" in content
    assert "game_id: fake_game" in content
    assert "fi_avg: 0.7" in content
    assert "sqi_avg: 0.9" in content
    assert "error_count: 0" in content
    assert "platform_report_status: not_applicable" in content
    assert "user_id: None" not in content
    assert "game_id: None" not in content
    assert "fi_avg: None" not in content
    assert "sqi_avg: None" not in content
    assert "error_count: None" not in content
