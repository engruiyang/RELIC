from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="mock", choices=["mock", "core", "core-control", "live-readonly", "live-control"])
    parser.add_argument("--db-path", default="data/relic_local.db")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--duration-sec", type=int, default=3)
    parser.add_argument("--user-id", default="demo_user")
    parser.add_argument("--game-id", default="fake_game")
    parser.add_argument("--task6b-config", default="config/task6b.yaml")
    args = parser.parse_args()

    try:
        from gui.qt_app import run_minimal_qt
    except (RuntimeError, ImportError):
        print("PySide6 is required for GUI. Install with: pip install PySide6")
        return 1

    if args.mode == "core":
        print(f"[GUI] mode=core db_path={args.db_path}", flush=True)
        print("[GUI] source=core_readonly", flush=True)
    elif args.mode == "core-control":
        print(f"[GUI] mode=core-control db_path={args.db_path}", flush=True)
        print("[GUI] source=core_control", flush=True)
    elif args.mode == "live-readonly":
        print(f"[GUI] mode=live-readonly db_path={args.db_path}", flush=True)
        print("[GUI] source=live_readonly", flush=True)
        print(f"[GUI LIVE] connecting {args.host}:{args.port}", flush=True)
    elif args.mode == "live-control":
        print(f"[GUI] mode=live-control db_path={args.db_path}", flush=True)
        print("[GUI] source=live_control", flush=True)
        print(f"[GUI LIVE] connecting {args.host}:{args.port}", flush=True)
    else:
        print("[GUI] mode=mock", flush=True)
        print("[GUI] source=mock", flush=True)

    try:
        return run_minimal_qt(mode=args.mode, db_path=args.db_path, duration_sec=args.duration_sec, user_id=args.user_id, game_id=args.game_id, task6b_config=args.task6b_config, host=args.host, port=args.port)
    except Exception as exc:
        if args.mode == "core":
            print(f"[GUI ERROR] failed to initialize core readonly source: {exc}", flush=True)
            print("Fallback to mock? no", flush=True)
            return 2
        raise


if __name__ == "__main__":
    sys.exit(main())
