from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from game.fake_game_client import FakeGameClient
from game.game_manager import GameManager
from game.game_manifest import GameManifest
from game.game_pipeline import GamePipelineRunner, LiveSnapshotProvider, MockSnapshotProvider
from runtime.local_runtime import LocalRuntime
from session.session_manager import SessionManager
from storage.storage_manager import StorageManager
from storage.sqlite_store import SqliteStore
from user.profile_manager import ProfileManager
from user.user_manager import UserManager
from ui_cli.evaluate_task6b import load_structured_file, _resolve_task6b_predictor_params


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["demo", "user"], default="demo")
    p.add_argument("--bridge", choices=["mock", "live"], default="mock")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--interval", type=float, default=1.0)
    p.add_argument("--print-jsonl", action="store_true")
    p.add_argument("--print-ticks", action="store_true")
    p.add_argument("--record-pipeline-jsonl")
    p.add_argument("--duration-sec", type=int, default=5)
    p.add_argument("--user-id", default="demo_user")
    p.add_argument("--db-path", default="data/relic_task8a.db")
    p.add_argument("--game-id", default="fake_game")
    p.add_argument("--task6b-config", default="config/task6b.yaml")
    return p


def main() -> None:
    a = build_parser().parse_args()
    store = SqliteStore(db_path=a.db_path)
    store.connect()
    task6b_cfg_raw = load_structured_file(a.task6b_config)
    task6b_cfg_active = _resolve_task6b_predictor_params(task6b_cfg_raw)
    session_manager = SessionManager(sqlite_store=store)
    ok, reason, session = session_manager.start_session(
        a.user_id,
        a.game_id,
        None,
        task6b_config_path=a.task6b_config,
        task6b_config_snapshot={
            "source": f"task8c_{a.bridge}",
            "task6b_config_loaded": bool(task6b_cfg_raw),
            "task6b_config_accepted": bool(task6b_cfg_raw.get("accepted", True)),
            "predictor_version": "task6b_predictor_v1",
            "active_params": task6b_cfg_active,
        },
    )
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
        description="Task8C headless fake game",
    )
    manager.register_game(manifest, FakeGameClient())
    manager.select_game("fake_game")
    manager.start_game(session.session_id)

    pipeline_path = a.record_pipeline_jsonl
    if pipeline_path is None and a.print_jsonl:
        pipeline_path = f"logs/game_debug/{session.session_id}.pipeline.jsonl"
    provider = MockSnapshotProvider()
    user_storage = None
    if a.bridge == "live":
        user_storage = StorageManager(sqlite_path=a.db_path)
        user_storage.initialize()
        um, pm = UserManager(user_storage.sqlite), ProfileManager(user_storage.sqlite)
        if a.mode == "demo":
            current_user = um.ensure_demo_user()
            user_profile = pm.get_profile(current_user["user_id"])
        else:
            current_user = um.load_user(a.user_id)
            if current_user is None:
                raise ValueError(f"user not found: {a.user_id}")
            user_profile = pm.get_profile(current_user["user_id"])
        provider = LiveSnapshotProvider(a.host, a.port, current_user=current_user, user_profile=user_profile, calibration_store=user_storage)
    runner = GamePipelineRunner(runtime=runtime, game_manager=manager, session_manager=session_manager, session_id=session.session_id, user_id=a.user_id, game_id=a.game_id, pipeline_jsonl_path=pipeline_path)

    try:
        ticks = max(1, int(a.duration_sec / max(a.interval, 1e-3)))
        now_ms = 0
        for _ in range(ticks):
            now_ms += int(a.interval * 1000)
            snap = provider.next_snapshot(now_ms)
            res = runner.process_snapshot(snap)
            if a.print_jsonl:
                print(json.dumps(res.to_dict(), ensure_ascii=False))
            elif a.print_ticks:
                print(f"tick={res.tick} attention={res.input.get('attention')} sqi={res.input.get('sqi')} fi_smoothed={res.input.get('fi_smoothed')} control_state={res.input.get('control_state')} score={res.output.get('score')} event_types={res.output.get('event_types')} feedback_hint={(res.view_state or {}).get('feedback_hint')}")
            time.sleep(a.interval)
    finally:
        runner.stop(reason="duration_reached")
        ended = session_manager.end_session(reason="task8c_debug_done")
        if hasattr(provider, "close"):
            provider.close()
        runner.close()
        if user_storage is not None:
            user_storage.shutdown()

    summary = store.get_training_session(session.session_id)
    print(json.dumps({
        "session_id": session.session_id,
        "task6b_config_path": a.task6b_config,
        "task6b_config_loaded": bool(task6b_cfg_raw),
        "task6b_config_accepted": bool(task6b_cfg_raw.get("accepted", True)),
        "predictor_version": "task6b_predictor_v1",
        "score": summary.get("score") if summary else None,
        "game_event_count": summary.get("game_event_count") if summary else None,
        "behavior_sample_count": summary.get("behavior_sample_count") if summary else None,
        "log_path": ended.log_path if ended else None,
        "summary": summary,
        "view_state": manager.get_current_view_state(),
    }, ensure_ascii=False))
    store.close()


if __name__ == "__main__":
    main()
