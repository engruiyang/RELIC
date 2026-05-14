from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="mock", choices=["mock", "core"])
    parser.add_argument("--db-path", default="data/relic_local.db")
    args = parser.parse_args()

    try:
        from gui.qt_app import run_minimal_qt
    except (RuntimeError, ImportError):
        print("PySide6 is required for GUI. Install with: pip install PySide6")
        return 1

    if args.mode == "core":
        print(f"[GUI] mode=core db_path={args.db_path}", flush=True)
        print("[GUI] source=core_readonly", flush=True)
    else:
        print("[GUI] mode=mock", flush=True)
        print("[GUI] source=mock", flush=True)

    try:
        return run_minimal_qt(mode=args.mode, db_path=args.db_path)
    except Exception as exc:
        if args.mode == "core":
            print(f"[GUI ERROR] failed to initialize core readonly source: {exc}", flush=True)
            print("Fallback to mock? no", flush=True)
            return 2
        raise


if __name__ == "__main__":
    sys.exit(main())
