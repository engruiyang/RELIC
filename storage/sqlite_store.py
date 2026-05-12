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
        conn.execute("""CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, display_name TEXT NOT NULL, user_type TEXT NOT NULL, created_at TEXT NOT NULL, last_login_at TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS user_profiles (user_id TEXT PRIMARY KEY, attention_low_threshold INTEGER NOT NULL, attention_high_threshold INTEGER NOT NULL, preferred_game_id TEXT NOT NULL, difficulty_level INTEGER NOT NULL, last_calibration_id TEXT, updated_at TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(user_id))""")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS calibration_profiles (
                calibration_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                device_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                calibration_type TEXT NOT NULL,
                attention_baseline REAL,
                attention_std REAL,
                attention_valid_sample_ratio REAL NOT NULL,
                gyro_bias_x REAL,
                gyro_bias_y REAL,
                gyro_bias_z REAL,
                gyro_noise_x REAL,
                gyro_noise_y REAL,
                gyro_noise_z REAL,
                gyro_noise_rms REAL,
                gyro_stability_score REAL NOT NULL,
                signal_quality_baseline REAL NOT NULL,
                valid INTEGER NOT NULL,
                failure_reason TEXT
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS training_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                game_id TEXT,
                calibration_id TEXT,
                started_at TEXT,
                ended_at TEXT,
                status TEXT,
                log_path TEXT,
                valid_duration_ms INTEGER,
                warning_duration_ms INTEGER,
                unreliable_duration_ms INTEGER,
                error_count INTEGER,
                final_fi_avg REAL,
                final_sqi_avg REAL,
                control_state_summary TEXT,
                score REAL,
                end_reason TEXT,
                estimator_version TEXT,
                task6b_config_path TEXT,
                task6b_config_snapshot TEXT,
                behavior_ready_ratio REAL,
                has_behavior_samples INTEGER
            )
            """
        )
        conn.commit()

    def upsert_user(self, user: dict[str, Any]) -> None:
        conn = self._ensure_conn()
        conn.execute("""INSERT INTO users (user_id, display_name, user_type, created_at, last_login_at) VALUES (:user_id, :display_name, :user_type, :created_at, :last_login_at) ON CONFLICT(user_id) DO UPDATE SET display_name=excluded.display_name, user_type=excluded.user_type, last_login_at=excluded.last_login_at""", user)
        conn.commit()

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        conn = self._ensure_conn()
        row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        return dict(row) if row else None

    def list_users(self) -> list[dict[str, Any]]:
        conn = self._ensure_conn()
        rows = conn.execute("SELECT * FROM users ORDER BY created_at").fetchall()
        return [dict(r) for r in rows]

    def list_users_by_type(self, user_type: str) -> list[dict[str, Any]]:
        conn = self._ensure_conn()
        rows = conn.execute("SELECT * FROM users WHERE user_type=? ORDER BY created_at", (user_type,)).fetchall()
        return [dict(r) for r in rows]

    def upsert_user_profile(self, profile: dict[str, Any]) -> None:
        conn = self._ensure_conn()
        conn.execute("""INSERT INTO user_profiles (user_id, attention_low_threshold, attention_high_threshold, preferred_game_id, difficulty_level, last_calibration_id, updated_at) VALUES (:user_id, :attention_low_threshold, :attention_high_threshold, :preferred_game_id, :difficulty_level, :last_calibration_id, :updated_at) ON CONFLICT(user_id) DO UPDATE SET attention_low_threshold=excluded.attention_low_threshold, attention_high_threshold=excluded.attention_high_threshold, preferred_game_id=excluded.preferred_game_id, difficulty_level=excluded.difficulty_level, last_calibration_id=excluded.last_calibration_id, updated_at=excluded.updated_at""", profile)
        conn.commit()

    def get_user_profile(self, user_id: str) -> dict[str, Any] | None:
        conn = self._ensure_conn()
        row = conn.execute("SELECT * FROM user_profiles WHERE user_id=?", (user_id,)).fetchone()
        return dict(row) if row else None

    def insert_calibration_profile(self, profile: dict[str, Any]) -> None:
        conn = self._ensure_conn()
        payload = dict(profile)
        payload["valid"] = 1 if payload.get("valid") else 0
        conn.execute(
            """
            INSERT INTO calibration_profiles (
                calibration_id, user_id, device_id, created_at, calibration_type,
                attention_baseline, attention_std, attention_valid_sample_ratio,
                gyro_bias_x, gyro_bias_y, gyro_bias_z,
                gyro_noise_x, gyro_noise_y, gyro_noise_z, gyro_noise_rms,
                gyro_stability_score, signal_quality_baseline, valid, failure_reason
            ) VALUES (
                :calibration_id, :user_id, :device_id, :created_at, :calibration_type,
                :attention_baseline, :attention_std, :attention_valid_sample_ratio,
                :gyro_bias_x, :gyro_bias_y, :gyro_bias_z,
                :gyro_noise_x, :gyro_noise_y, :gyro_noise_z, :gyro_noise_rms,
                :gyro_stability_score, :signal_quality_baseline, :valid, :failure_reason
            )
            """,
            payload,
        )
        conn.commit()

    def get_calibration_profile(self, calibration_id: str) -> dict[str, Any] | None:
        conn = self._ensure_conn()
        row = conn.execute("SELECT * FROM calibration_profiles WHERE calibration_id=?", (calibration_id,)).fetchone()
        return dict(row) if row else None

    def list_calibration_profiles(self, user_id: str) -> list[dict[str, Any]]:
        conn = self._ensure_conn()
        rows = conn.execute("SELECT * FROM calibration_profiles WHERE user_id=? ORDER BY created_at", (user_id,)).fetchall()
        return [dict(r) for r in rows]


    def get_latest_calibration_profile(self, user_id: str) -> dict[str, Any] | None:
        conn = self._ensure_conn()
        row = conn.execute("SELECT * FROM calibration_profiles WHERE user_id=? ORDER BY created_at DESC LIMIT 1", (user_id,)).fetchone()
        return dict(row) if row else None

    def list_calibration_profiles(self, user_id: str) -> list[dict[str, Any]]:
        conn = self._ensure_conn()
        rows = conn.execute("SELECT * FROM calibration_profiles WHERE user_id=? ORDER BY created_at", (user_id,)).fetchall()
        return [dict(r) for r in rows]


    def get_latest_calibration_profile(self, user_id: str) -> dict[str, Any] | None:
        conn = self._ensure_conn()
        row = conn.execute("SELECT * FROM calibration_profiles WHERE user_id=? ORDER BY created_at DESC LIMIT 1", (user_id,)).fetchone()
        return dict(row) if row else None

    def list_calibration_profiles(self, user_id: str) -> list[dict[str, Any]]:
        conn = self._ensure_conn()
        rows = conn.execute("SELECT * FROM calibration_profiles WHERE user_id=? ORDER BY created_at", (user_id,)).fetchall()
        return [dict(r) for r in rows]


    def upsert_training_session(self, summary: dict[str, Any]) -> None:
        conn = self._ensure_conn()
        conn.execute(
            """
            INSERT INTO training_sessions (
                session_id, user_id, game_id, calibration_id, started_at, ended_at, status, log_path,
                valid_duration_ms, warning_duration_ms, unreliable_duration_ms, error_count,
                final_fi_avg, final_sqi_avg, control_state_summary, score, end_reason,
                estimator_version, task6b_config_path, task6b_config_snapshot,
                behavior_ready_ratio, has_behavior_samples
            ) VALUES (
                :session_id, :user_id, :game_id, :calibration_id, :started_at, :ended_at, :status, :log_path,
                :valid_duration_ms, :warning_duration_ms, :unreliable_duration_ms, :error_count,
                :final_fi_avg, :final_sqi_avg, :control_state_summary, :score, :end_reason,
                :estimator_version, :task6b_config_path, :task6b_config_snapshot,
                :behavior_ready_ratio, :has_behavior_samples
            )
            ON CONFLICT(session_id) DO UPDATE SET
                ended_at=excluded.ended_at,
                status=excluded.status,
                valid_duration_ms=excluded.valid_duration_ms,
                warning_duration_ms=excluded.warning_duration_ms,
                unreliable_duration_ms=excluded.unreliable_duration_ms,
                error_count=excluded.error_count,
                final_fi_avg=excluded.final_fi_avg,
                final_sqi_avg=excluded.final_sqi_avg,
                control_state_summary=excluded.control_state_summary,
                score=excluded.score,
                end_reason=excluded.end_reason,
                behavior_ready_ratio=excluded.behavior_ready_ratio,
                has_behavior_samples=excluded.has_behavior_samples
            """,
            summary,
        )
        conn.commit()

    def get_training_session(self, session_id: str) -> dict[str, Any] | None:
        conn = self._ensure_conn()
        row = conn.execute("SELECT * FROM training_sessions WHERE session_id=?", (session_id,)).fetchone()
        return dict(row) if row else None
