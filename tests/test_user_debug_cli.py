from __future__ import annotations

import sqlite3

from ui_cli.run_user_debug import run_user_debug


def test_demo_first_run_creates_user_and_profile(tmp_path, capsys):
    db = tmp_path / "u.db"
    out = run_user_debug(mode="demo", db_path=str(db))
    printed = capsys.readouterr().out

    assert out["current_user_id"] == "demo"
    assert out["profile_loaded"] is True
    assert "db_path=" in printed
    assert "profile.attention_low_threshold=" in printed
    assert out["system_state"] == "USER_READY"


def test_demo_second_run_reuses_single_demo(tmp_path):
    db = tmp_path / "u.db"
    run_user_debug(mode="demo", db_path=str(db))
    run_user_debug(mode="demo", db_path=str(db))

    conn = sqlite3.connect(str(db))
    count = conn.execute("SELECT COUNT(*) FROM users WHERE user_type='demo'").fetchone()[0]
    assert count == 1


def test_guest_mode_available_and_not_break_demo(tmp_path):
    db = tmp_path / "u.db"
    run_user_debug(mode="demo", db_path=str(db))
    out = run_user_debug(mode="guest", db_path=str(db))

    assert out["user_type"] == "guest"
    assert out["persisted"] is False
    assert out["profile_loaded"] is False

    conn = sqlite3.connect(str(db))
    count = conn.execute("SELECT COUNT(*) FROM users WHERE user_type='demo'").fetchone()[0]
    assert count == 1


def test_custom_db_path_does_not_pollute_default(tmp_path):
    custom = tmp_path / "custom.db"
    run_user_debug(mode="demo", db_path=str(custom))

    conn = sqlite3.connect(str(custom))
    count = conn.execute("SELECT COUNT(*) FROM users WHERE user_type='demo'").fetchone()[0]
    assert count == 1
