from __future__ import annotations

import sqlite3

from ui_cli.run_user_debug import run_user_debug
from user.user_manager import UserManager
from storage.storage_manager import StorageManager


def test_create_local_user_then_list(tmp_path):
    db = tmp_path / 'u.db'
    storage = StorageManager(sqlite_path=str(db)); storage.initialize()
    um = UserManager(storage.sqlite)
    user, created = um.create_local_user_if_absent('alice', 'Alice')
    users = um.list_users()
    storage.shutdown()

    assert created is True
    assert user['user_id'] == 'alice'
    assert any(u['user_id'] == 'alice' for u in users)


def test_select_user_loads_profile(tmp_path):
    db = tmp_path / 'u.db'
    storage = StorageManager(sqlite_path=str(db)); storage.initialize()
    um = UserManager(storage.sqlite)
    um.create_local_user_if_absent('alice', 'Alice')
    storage.shutdown()

    out = run_user_debug(mode='user', db_path=str(db), user_id='alice')
    assert out['current_user_id'] == 'alice'
    assert out['profile_loaded'] is True


def test_duplicate_user_id_not_duplicated(tmp_path):
    db = tmp_path / 'u.db'
    storage = StorageManager(sqlite_path=str(db)); storage.initialize()
    um = UserManager(storage.sqlite)
    _, c1 = um.create_local_user_if_absent('alice', 'Alice')
    _, c2 = um.create_local_user_if_absent('alice', 'Alice 2')
    storage.shutdown()

    conn = sqlite3.connect(str(db))
    count = conn.execute("SELECT COUNT(*) FROM users WHERE user_id='alice'").fetchone()[0]
    assert c1 is True and c2 is False
    assert count == 1


def test_guest_mode_does_not_write_users_table(tmp_path):
    db = tmp_path / 'u.db'
    run_user_debug(mode='guest', db_path=str(db))
    conn = sqlite3.connect(str(db))
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert count == 0
