from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class SqliteStore:
    def __init__(self, db_path: str = "data/relic_local.db"):
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _ensure_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self.connect()
        return self._conn

    def _init_schema(self) -> None:
        conn = self._ensure_conn()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                user_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                attention_low_threshold INTEGER NOT NULL,
                attention_high_threshold INTEGER NOT NULL,
                preferred_game_id TEXT NOT NULL,
                difficulty_level INTEGER NOT NULL,
                last_calibration_id TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
            """
        )
        conn.commit()

    def upsert_user(self, user: dict[str, Any]) -> None:
        conn = self._ensure_conn()
        conn.execute(
            """
            INSERT INTO users (user_id, display_name, user_type, created_at, last_login_at)
            VALUES (:user_id, :display_name, :user_type, :created_at, :last_login_at)
            ON CONFLICT(user_id) DO UPDATE SET
                display_name=excluded.display_name,
                user_type=excluded.user_type,
                last_login_at=excluded.last_login_at
            """,
            user,
        )
        conn.commit()

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        conn = self._ensure_conn()
        row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        return dict(row) if row else None

    def list_users_by_type(self, user_type: str) -> list[dict[str, Any]]:
        conn = self._ensure_conn()
        rows = conn.execute("SELECT * FROM users WHERE user_type=? ORDER BY created_at", (user_type,)).fetchall()
        return [dict(r) for r in rows]

    def upsert_user_profile(self, profile: dict[str, Any]) -> None:
        conn = self._ensure_conn()
        conn.execute(
            """
            INSERT INTO user_profiles (
                user_id, attention_low_threshold, attention_high_threshold,
                preferred_game_id, difficulty_level, last_calibration_id, updated_at
            ) VALUES (
                :user_id, :attention_low_threshold, :attention_high_threshold,
                :preferred_game_id, :difficulty_level, :last_calibration_id, :updated_at
            )
            ON CONFLICT(user_id) DO UPDATE SET
                attention_low_threshold=excluded.attention_low_threshold,
                attention_high_threshold=excluded.attention_high_threshold,
                preferred_game_id=excluded.preferred_game_id,
                difficulty_level=excluded.difficulty_level,
                last_calibration_id=excluded.last_calibration_id,
                updated_at=excluded.updated_at
            """,
            profile,
        )
        conn.commit()

    def get_user_profile(self, user_id: str) -> dict[str, Any] | None:
        conn = self._ensure_conn()
        row = conn.execute("SELECT * FROM user_profiles WHERE user_id=?", (user_id,)).fetchone()
        return dict(row) if row else None
