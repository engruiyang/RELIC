from __future__ import annotations

import sqlite3

from core.app_controller import AppController
from storage.sqlite_store import SqliteStore
from user.profile_manager import ProfileManager
from user.user_manager import UserManager


def test_first_start_creates_demo_user_and_profile(tmp_path):
    db_path = tmp_path / "relic_local.db"
    app = AppController()
    app.storage = app.storage.__class__(sqlite_path=str(db_path))
    app.user_manager = UserManager(app.storage.sqlite)
    app.profile_manager = ProfileManager(app.storage.sqlite)

    app.start(ticks=0, debug=False)

    store = SqliteStore(str(db_path))
    store.connect()
    demo = store.get_user("demo")
    profile = store.get_user_profile("demo")

    assert demo is not None
    assert profile is not None
    assert app.user_manager.current_user is not None
    assert app.user_manager.current_user["user_id"] == "demo"


def test_restart_loads_single_demo_and_updates_last_login(tmp_path):
    db_path = tmp_path / "relic_local.db"

    app1 = AppController()
    app1.storage = app1.storage.__class__(sqlite_path=str(db_path))
    app1.user_manager = UserManager(app1.storage.sqlite)
    app1.profile_manager = ProfileManager(app1.storage.sqlite)
    app1.start(ticks=0, debug=False)
    first_login = app1.user_manager.current_user["last_login_at"]

    app2 = AppController()
    app2.storage = app2.storage.__class__(sqlite_path=str(db_path))
    app2.user_manager = UserManager(app2.storage.sqlite)
    app2.profile_manager = ProfileManager(app2.storage.sqlite)
    app2.start(ticks=0, debug=False)
    second_login = app2.user_manager.current_user["last_login_at"]

    conn = sqlite3.connect(str(db_path))
    count = conn.execute("SELECT COUNT(*) FROM users WHERE user_type='demo'").fetchone()[0]

    assert count == 1
    assert second_login >= first_login
    assert app2.profile_manager.load_profile("demo")["user_id"] == "demo"


def test_guest_mode_does_not_break_demo_user(tmp_path):
    db_path = tmp_path / "relic_local.db"
    store = SqliteStore(str(db_path))
    store.connect()
    um = UserManager(store)
    pm = ProfileManager(store)

    demo = um.ensure_demo_user()
    pm.load_profile(demo["user_id"])
    guest = um.enter_guest_mode()

    assert guest["user_type"] == "guest"
    assert guest["user_id"] == "guest"
    assert store.get_user("demo") is not None


def test_default_profile_values(tmp_path):
    db_path = tmp_path / "relic_local.db"
    store = SqliteStore(str(db_path))
    store.connect()
    um = UserManager(store)
    pm = ProfileManager(store)

    user = um.create_local_user("u1", "User1")
    profile = pm.load_profile(user["user_id"])

    assert profile["attention_low_threshold"] == 40
    assert profile["attention_high_threshold"] == 70
    assert profile["difficulty_level"] == 1
    assert "last_calibration_id" in profile
    assert profile["last_calibration_id"] is None
