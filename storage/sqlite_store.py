from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

TRAINING_SESSION_COLUMNS: list[tuple[str, str]] = [
    ("session_id", "TEXT PRIMARY KEY"),
    ("user_id", "TEXT"), ("game_id", "TEXT"), ("calibration_id", "TEXT"), ("started_at", "TEXT"), ("ended_at", "TEXT"), ("status", "TEXT"), ("log_path", "TEXT"),
    ("valid_duration_ms", "INTEGER"), ("warning_duration_ms", "INTEGER"), ("unreliable_duration_ms", "INTEGER"), ("error_count", "INTEGER"),
    ("final_fi_avg", "REAL"), ("final_sqi_avg", "REAL"), ("control_state_summary", "TEXT"), ("score", "REAL"), ("end_reason", "TEXT"),
    ("estimator_version", "TEXT"), ("task6b_config_path", "TEXT"), ("task6b_config_snapshot", "TEXT"), ("behavior_ready_ratio", "REAL"), ("has_behavior_samples", "INTEGER"),
    ("total_duration_ms", "INTEGER"), ("observed_tick_count", "INTEGER"), ("valid_tick_count", "INTEGER"), ("warning_tick_count", "INTEGER"), ("unreliable_tick_count", "INTEGER"),
    ("quality_state_summary", "TEXT"), ("quality_state_duration_summary", "TEXT"), ("control_state_duration_summary", "TEXT"),
    ("fi_min", "REAL"), ("fi_max", "REAL"), ("fi_last", "REAL"), ("sqi_min", "REAL"), ("sqi_max", "REAL"), ("sqi_last", "REAL"),
    ("game_event_count", "INTEGER"), ("score_update_count", "INTEGER"), ("behavior_sample_count", "INTEGER"), ("user_action_count", "INTEGER"), ("game_error_count", "INTEGER"),
    ("score_last", "REAL"), ("score_max", "REAL"), ("score_total_delta", "REAL"), ("game_completed", "INTEGER"), ("game_completion_reason", "TEXT"),
]


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
            self._conn.close(); self._conn = None

    def _ensure_conn(self) -> sqlite3.Connection:
        if self._conn is None: self.connect()
        return self._conn

    def _init_schema(self) -> None:
        conn = self._ensure_conn()
        conn.execute("""CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, display_name TEXT NOT NULL, user_type TEXT NOT NULL, created_at TEXT NOT NULL, last_login_at TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS user_profiles (user_id TEXT PRIMARY KEY, attention_low_threshold INTEGER NOT NULL, attention_high_threshold INTEGER NOT NULL, preferred_game_id TEXT NOT NULL, difficulty_level INTEGER NOT NULL, last_calibration_id TEXT, updated_at TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(user_id))""")
        conn.execute("""CREATE TABLE IF NOT EXISTS calibration_profiles (calibration_id TEXT PRIMARY KEY,user_id TEXT NOT NULL,device_id TEXT NOT NULL,created_at TEXT NOT NULL,calibration_type TEXT NOT NULL,attention_baseline REAL,attention_std REAL,attention_valid_sample_ratio REAL NOT NULL,gyro_bias_x REAL,gyro_bias_y REAL,gyro_bias_z REAL,gyro_noise_x REAL,gyro_noise_y REAL,gyro_noise_z REAL,gyro_noise_rms REAL,gyro_stability_score REAL NOT NULL,signal_quality_baseline REAL NOT NULL,valid INTEGER NOT NULL,failure_reason TEXT)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS training_sessions (session_id TEXT PRIMARY KEY)""")
        self._ensure_training_sessions_columns(conn)
        conn.commit()

    def _ensure_training_sessions_columns(self, conn: sqlite3.Connection) -> None:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(training_sessions)").fetchall()}
        for name, typ in TRAINING_SESSION_COLUMNS:
            if name not in cols:
                conn.execute(f"ALTER TABLE training_sessions ADD COLUMN {name} {typ}")

    def upsert_user(self, user: dict[str, Any]) -> None:
        c = self._ensure_conn(); c.execute("""INSERT INTO users (user_id, display_name, user_type, created_at, last_login_at) VALUES (:user_id,:display_name,:user_type,:created_at,:last_login_at) ON CONFLICT(user_id) DO UPDATE SET display_name=excluded.display_name,user_type=excluded.user_type,last_login_at=excluded.last_login_at""", user); c.commit()
    def get_user(self, user_id: str) -> dict[str, Any] | None:
        r = self._ensure_conn().execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone(); return dict(r) if r else None
    def list_users(self) -> list[dict[str, Any]]:
        return [dict(r) for r in self._ensure_conn().execute("SELECT * FROM users ORDER BY created_at").fetchall()]
    def list_users_by_type(self, user_type: str) -> list[dict[str, Any]]:
        return [dict(r) for r in self._ensure_conn().execute("SELECT * FROM users WHERE user_type=? ORDER BY created_at", (user_type,)).fetchall()]
    def upsert_user_profile(self, profile: dict[str, Any]) -> None:
        c=self._ensure_conn(); c.execute("""INSERT INTO user_profiles (user_id,attention_low_threshold,attention_high_threshold,preferred_game_id,difficulty_level,last_calibration_id,updated_at) VALUES (:user_id,:attention_low_threshold,:attention_high_threshold,:preferred_game_id,:difficulty_level,:last_calibration_id,:updated_at) ON CONFLICT(user_id) DO UPDATE SET attention_low_threshold=excluded.attention_low_threshold,attention_high_threshold=excluded.attention_high_threshold,preferred_game_id=excluded.preferred_game_id,difficulty_level=excluded.difficulty_level,last_calibration_id=excluded.last_calibration_id,updated_at=excluded.updated_at""", profile); c.commit()
    def get_user_profile(self, user_id: str) -> dict[str, Any] | None:
        r=self._ensure_conn().execute("SELECT * FROM user_profiles WHERE user_id=?", (user_id,)).fetchone(); return dict(r) if r else None
    def insert_calibration_profile(self, profile: dict[str, Any]) -> None:
        c=self._ensure_conn(); p=dict(profile); p["valid"]=1 if p.get("valid") else 0; c.execute("""INSERT INTO calibration_profiles (calibration_id,user_id,device_id,created_at,calibration_type,attention_baseline,attention_std,attention_valid_sample_ratio,gyro_bias_x,gyro_bias_y,gyro_bias_z,gyro_noise_x,gyro_noise_y,gyro_noise_z,gyro_noise_rms,gyro_stability_score,signal_quality_baseline,valid,failure_reason) VALUES (:calibration_id,:user_id,:device_id,:created_at,:calibration_type,:attention_baseline,:attention_std,:attention_valid_sample_ratio,:gyro_bias_x,:gyro_bias_y,:gyro_bias_z,:gyro_noise_x,:gyro_noise_y,:gyro_noise_z,:gyro_noise_rms,:gyro_stability_score,:signal_quality_baseline,:valid,:failure_reason)""", p); c.commit()
    def get_calibration_profile(self, calibration_id: str) -> dict[str, Any] | None:
        r=self._ensure_conn().execute("SELECT * FROM calibration_profiles WHERE calibration_id=?", (calibration_id,)).fetchone(); return dict(r) if r else None
    def list_calibration_profiles(self, user_id: str) -> list[dict[str, Any]]:
        return [dict(r) for r in self._ensure_conn().execute("SELECT * FROM calibration_profiles WHERE user_id=? ORDER BY created_at", (user_id,)).fetchall()]
    def get_latest_calibration_profile(self, user_id: str) -> dict[str, Any] | None:
        r=self._ensure_conn().execute("SELECT * FROM calibration_profiles WHERE user_id=? ORDER BY created_at DESC LIMIT 1", (user_id,)).fetchone(); return dict(r) if r else None

    def upsert_training_session(self, summary: dict[str, Any]) -> None:
        conn = self._ensure_conn()
        column_names = [name for name, _ in TRAINING_SESSION_COLUMNS]
        payload = {name: summary.get(name) for name in column_names}
        cols = ",".join(column_names)
        vals = ",".join([f":{k}" for k in column_names])
        updates = ",".join([f"{k}=excluded.{k}" for k in column_names if k != "session_id"])
        conn.execute(f"INSERT INTO training_sessions ({cols}) VALUES ({vals}) ON CONFLICT(session_id) DO UPDATE SET {updates}", payload)
        conn.commit()

    def get_training_session(self, session_id: str) -> dict[str, Any] | None:
        r = self._ensure_conn().execute("SELECT * FROM training_sessions WHERE session_id=?", (session_id,)).fetchone()
        return dict(r) if r else None

    def list_training_sessions(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = self._ensure_conn().execute("SELECT * FROM training_sessions ORDER BY started_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]
