from __future__ import annotations

import argparse
import json

from game.fake_game_client import FakeGameClient
from game.game_manager import GameManager
from game.game_manifest import GameManifest
from runtime.local_runtime import LocalRuntime
from runtime.runtime_messages import RuntimeSnapshotView
from session.session_manager import SessionManager
from storage.sqlite_store import SqliteStore


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["demo", "user"], default="demo")
    p.add_argument("--duration-sec", type=int, default=5)
    p.add_argument("--user-id", default="demo_user")
    p.add_argument("--db-path", default="data/relic_task8a.db")
    p.add_argument("--game-id", default="fake_game")
    return p


def main() -> None:
    a = build_parser().parse_args()
    store = SqliteStore(db_path=a.db_path)
    store.connect()
    session_manager = SessionManager(sqlite_store=store)
    ok, reason, session = session_manager.start_session(a.user_id, a.game_id, None, task6b_config_path="config/task6b.yaml", task6b_config_snapshot={"source": "task8a_debug"})
    if not ok or not session:
        print(f"start_session failed: {reason}")
        store.close()
        return

    runtime = LocalRuntime()
    manager = GameManager(runtime=runtime, session_manager=session_manager)
    manifest = GameManifest(
        game_id="fake_game",
        display_name="Fake Game Headless",
        version="0.1.0",
        supported_event_types=["score_update", "behavior_sample", "difficulty_request", "game_completed", "game_error", "user_action"],
        supported_command_types=["start_game", "pause_game", "resume_game", "stop_game", "set_difficulty", "set_feedback_mode"],
        min_duration_sec=1,
        max_duration_sec=300,
        requires_behavior_sample=True,
        description="Task8A headless fake game",
    )
    manager.register_game(manifest, FakeGameClient())
    manager.select_game("fake_game")
    manager.start_game(session.session_id)

    states = ["STABLE_FOCUS", "HIGH_FOCUS", "DISTRACTED", "UNRELIABLE_SIGNAL"]
    for i in range(a.duration_sec):
        control_state = states[i % len(states)]
        runtime.publish_snapshot(
            RuntimeSnapshotView(
                session_id=session.session_id,
                user_id=a.user_id,
                game_id=a.game_id,
                now_ms=i * 1000,
                fi_valid=True,
                fi_smoothed=0.7,
                sqi=0.9,
                control_state=control_state,
                quality_state="ok" if i % 3 else "warning",
                attention_fresh=True,
                behavior_ready=True,
                delta_ms=1000,
            )
        )
        session_manager.record_runtime_snapshot(
            {
                "session_id": session.session_id,
                "user_id": a.user_id,
                "game_id": a.game_id,
                "quality_state": "ok" if i % 3 else "warning",
                "fi_valid": True,
                "fi_smoothed": 0.7,
                "sqi": 0.9,
                "control_state": control_state,
                "behavior_ready": True,
                "delta_ms": 1000,
                "warning_flags": [],
                "error_flags": [],
            }
        )

    manager.stop_game(issued_at_ms=a.duration_sec * 1000)
    ended = session_manager.end_session(reason="task8a_debug_done")
    summary = store.get_training_session(session.session_id)
    print(json.dumps({
        "session_id": session.session_id,
        "score": summary.get("score") if summary else None,
        "game_event_count": summary.get("game_event_count") if summary else None,
        "behavior_sample_count": summary.get("behavior_sample_count") if summary else None,
        "log_path": ended.log_path if ended else None,
        "summary": summary,
        "view_state": manager.get_current_view_state(),
    }, ensure_ascii=False, indent=2))
    store.close()


if __name__ == "__main__":
    main()
