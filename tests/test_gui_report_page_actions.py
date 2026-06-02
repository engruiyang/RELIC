from pathlib import Path
import sqlite3

from gui.gui_facade import GuiFacade


def test_report_page_actions_feedback(tmp_path: Path) -> None:
    db = tmp_path / "reports.db"
    report_dir = tmp_path / "reports" / "sessions"
    report_dir.mkdir(parents=True)
    report_path = report_dir / "session_TEST_001.md"
    report_path.write_text("# RELIC Link Diagnostics\n\n- session_id: session_TEST_001\n- user_id: TEST\n", encoding="utf-8")
    conn = sqlite3.connect(db)
    conn.execute(
        "CREATE TABLE training_sessions (session_id TEXT, user_id TEXT, game_id TEXT, status TEXT, score REAL, report_path TEXT, log_path TEXT, started_at TEXT, ended_at TEXT, total_duration_ms INTEGER, behavior_sample_count INTEGER, game_event_count INTEGER, warning_count INTEGER, error_count INTEGER)"
    )
    conn.execute(
        "INSERT INTO training_sessions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("session_TEST_001", "TEST", "trace_lock", "ended", 12.5, str(report_path), "logs/sessions/session_TEST_001.jsonl", "2026-05-31T00:00:00Z", "2026-05-31T00:01:00Z", 60000, 3, 9, 0, 0),
    )
    conn.commit()
    conn.close()

    f = GuiFacade(mode="mock", db_path=str(db), user_id="TEST")
    refresh = f.invoke_action("report.refresh", {"user_id": "TEST"})
    assert refresh.get("status") == "accepted"
    assert refresh.get("message") == "report_refreshed"
    assert isinstance(refresh.get("result"), dict)

    latest = f.invoke_action("report.latest", {"user_id": "TEST"})
    assert latest.get("status") == "accepted"
    assert latest.get("session_id") == "session_TEST_001"

    listing = f.invoke_action("report.list", {"user_id": "TEST"})
    assert listing.get("status") == "accepted"
    assert listing.get("items_count") == 1
    assert listing["items"][0]["user_id"] == "TEST"
    assert "session_TEST_001" in listing.get("report_list_text", "")

    missing = f.invoke_action("report.show", {"user_id": "TEST"})
    assert missing.get("status") == "missing_input"
    assert missing.get("message") in {"missing_session_id", "missing_report_identifier"}

    shown = f.invoke_action("report.show", {"user_id": "TEST", "session_id": "session_TEST_001"})
    assert shown.get("status") == "accepted"
    assert "RELIC Link Diagnostics" in shown.get("detail", {}).get("report_preview", "")

    exported = f.invoke_action("report.export_txt", {"user_id": "TEST", "session_id": "session_TEST_001", "out_dir": str(tmp_path / "exports")})
    assert exported.get("status") == "accepted"
    export_path = Path(exported.get("export_path") or exported.get("result", {}).get("export_path"))
    assert export_path.exists()
    assert export_path.suffix == ".txt"
    assert "RELIC Link Diagnostics" in export_path.read_text(encoding="utf-8")


def test_report_show_unknown_session_is_visible() -> None:
    f = GuiFacade(mode="mock")
    result = f.invoke_action("report.show", {"user_id": "TEST", "session_id": "NO_SUCH_SESSION"})
    assert result.get("status") == "session_not_found"
    assert result.get("session_id") == "NO_SUCH_SESSION"


def test_report_scope_rejects_other_user_report(tmp_path: Path) -> None:
    db = tmp_path / "reports.db"
    report_path = tmp_path / "other.md"
    report_path.write_text("# Other User Report\n", encoding="utf-8")
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE training_sessions (session_id TEXT, user_id TEXT, game_id TEXT, status TEXT, report_path TEXT)")
    conn.execute("INSERT INTO training_sessions VALUES (?,?,?,?,?)", ("session_OTHER", "OTHER", "trace_lock", "ended", str(report_path)))
    conn.commit()
    conn.close()

    f = GuiFacade(mode="mock", db_path=str(db), user_id="TEST")
    listing = f.invoke_action("report.list", {"user_id": "TEST"})
    assert listing.get("items_count") == 0
    result = f.invoke_action("report.show", {"user_id": "TEST", "session_id": "session_OTHER"})
    assert result.get("status") == "session_not_found"


def test_report_latest_prefers_readable_report_over_newer_no_report(tmp_path: Path) -> None:
    db = tmp_path / "reports.db"
    report_path = tmp_path / "reports" / "sessions" / "session_TEST_report.md"
    report_path.parent.mkdir(parents=True)
    report_path.write_text("# RELIC Link Diagnostics\n\n- session_id: session_TEST_report\n- user_id: TEST\n", encoding="utf-8")
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE training_sessions (session_id TEXT, user_id TEXT, game_id TEXT, status TEXT, report_path TEXT, log_path TEXT, started_at TEXT, ended_at TEXT)")
    conn.execute("INSERT INTO training_sessions VALUES (?,?,?,?,?,?,?,?)", ("session_TEST_no_report", "TEST", "fake_game", "ended", "", "logs/sessions/session_TEST_no_report.jsonl", "2026-06-01T00:00:00Z", "2026-06-01T00:01:00Z"))
    conn.execute("INSERT INTO training_sessions VALUES (?,?,?,?,?,?,?,?)", ("session_TEST_report", "TEST", "trace_lock", "ended", str(report_path), "logs/sessions/session_TEST_report.jsonl", "2026-05-31T00:00:00Z", "2026-05-31T00:01:00Z"))
    conn.commit()
    conn.close()

    f = GuiFacade(mode="mock", db_path=str(db), user_id="TEST")
    latest = f.invoke_action("report.latest", {"user_id": "TEST"})
    assert latest.get("status") == "accepted"
    assert latest.get("session_id") == "session_TEST_report"
    assert latest.get("report_path") == str(report_path)
    assert "RELIC Link Diagnostics" in latest.get("report_preview", "")

    shown = f.invoke_action("report.show", {"user_id": "TEST", "session_id": "session_TEST_no_report", "allow_latest_fallback": True})
    assert shown.get("status") == "accepted"
    assert shown.get("session_id") == "session_TEST_report"
    assert shown.get("report_path") == str(report_path)


def test_report_infers_default_report_path_when_db_path_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    db = tmp_path / "reports.db"
    report_path = tmp_path / "reports" / "sessions" / "session_TEST_inferred.md"
    report_path.parent.mkdir(parents=True)
    report_path.write_text("# RELIC Link Diagnostics\n\n- session_id: session_TEST_inferred\n- user_id: TEST\n", encoding="utf-8")
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE training_sessions (session_id TEXT, user_id TEXT, game_id TEXT, status TEXT, report_path TEXT, log_path TEXT, started_at TEXT, ended_at TEXT)")
    conn.execute("INSERT INTO training_sessions VALUES (?,?,?,?,?,?,?,?)", ("session_TEST_inferred", "TEST", "trace_lock", "ended", "", "logs/sessions/session_TEST_inferred.jsonl", "2026-05-31T00:00:00Z", "2026-05-31T00:01:00Z"))
    conn.commit()
    conn.close()

    f = GuiFacade(mode="mock", db_path=str(db), user_id="TEST")
    latest = f.invoke_action("report.latest", {"user_id": "TEST"})
    assert latest.get("status") == "accepted"
    assert latest.get("session_id") == "session_TEST_inferred"
    assert latest.get("report_path") == "reports/sessions/session_TEST_inferred.md"
    assert "RELIC Link Diagnostics" in latest.get("report_preview", "")

    exported = f.invoke_action("report.export_txt", {"user_id": "TEST", "session_id": "session_TEST_inferred"})
    assert exported.get("status") == "accepted"
    assert Path(exported.get("export_path") or exported.get("result", {}).get("export_path")).exists()


def test_report_export_path_is_cleared_after_non_export_report_action(tmp_path: Path) -> None:
    db = tmp_path / "reports.db"
    report_dir = tmp_path / "reports" / "sessions"
    report_dir.mkdir(parents=True)
    report_path = report_dir / "session_TEST_clear.md"
    report_path.write_text("# RELIC Link Diagnostics\n\n- session_id: session_TEST_clear\n- user_id: TEST\n", encoding="utf-8")
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE training_sessions (session_id TEXT, user_id TEXT, game_id TEXT, status TEXT, report_path TEXT, started_at TEXT, ended_at TEXT)")
    conn.execute("INSERT INTO training_sessions VALUES (?,?,?,?,?,?,?)", ("session_TEST_clear", "TEST", "trace_lock", "ended", str(report_path), "2026-05-31T00:00:00Z", "2026-05-31T00:01:00Z"))
    conn.commit()
    conn.close()

    f = GuiFacade(mode="mock", db_path=str(db), user_id="TEST")
    exported = f.invoke_action("report.export_txt", {"user_id": "TEST", "session_id": "session_TEST_clear", "out_dir": str(tmp_path / "exports")})
    assert exported.get("status") == "accepted"
    assert f.get_control_state().get("report_export_path")

    shown = f.invoke_action("report.show", {"user_id": "TEST", "session_id": "session_TEST_clear"})
    assert shown.get("status") == "accepted"
    assert f.get_control_state().get("report_export_path") == ""


def test_report_list_text_includes_more_than_ten_reports(tmp_path: Path) -> None:
    db = tmp_path / "reports.db"
    report_dir = tmp_path / "reports" / "sessions"
    report_dir.mkdir(parents=True)
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE training_sessions (session_id TEXT, user_id TEXT, game_id TEXT, status TEXT, score REAL, report_path TEXT, log_path TEXT, started_at TEXT, ended_at TEXT)")
    for i in range(12):
        session_id = f"training_TEST_20260522_{140000 + i:06d}"
        report_path = report_dir / f"{session_id}.md"
        report_path.write_text(f"# RELIC Link Diagnostics\n\n- session_id: {session_id}\n- user_id: TEST\n", encoding="utf-8")
        conn.execute(
            "INSERT INTO training_sessions VALUES (?,?,?,?,?,?,?,?,?)",
            (session_id, "TEST", "trace_lock", "ended", float(i), str(report_path), f"logs/sessions/{session_id}.jsonl", f"2026-05-22T14:{i:02d}:00Z", f"2026-05-22T14:{i:02d}:30Z"),
        )
    conn.commit()
    conn.close()

    f = GuiFacade(mode="mock", db_path=str(db), user_id="TEST")
    listing = f.invoke_action("report.list", {"user_id": "TEST"})
    assert listing.get("status") == "accepted"
    assert listing.get("items_count") == 12
    text = listing.get("report_list_text", "")
    # The report list is intentionally displayed newest-first, so this test
    # should verify that all reports are present rather than pinning the
    # oldest report to row 1. This catches accidental truncation to the first
    # ten rows without fighting the UI sort order.
    for i in range(12):
        assert f"training_TEST_20260522_{140000 + i:06d}" in text
    assert "1. training_TEST_20260522_140011" in text
    assert "10. training_TEST_20260522_140002" in text
    assert "11. training_TEST_20260522_140001" in text
    assert "12. training_TEST_20260522_140000" in text
