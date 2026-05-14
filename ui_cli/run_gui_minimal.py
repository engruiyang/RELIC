from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="mock")
    args = parser.parse_args()

    try:
        from gui.qt_app import run_minimal_qt
    except RuntimeError:
        print("PySide6 is required for GUI. Install with: pip install PySide6")
        return 1
    except ImportError:
        print("PySide6 is required for GUI. Install with: pip install PySide6")
        return 1

    return run_minimal_qt(mode=args.mode)


if __name__ == "__main__":
    sys.exit(main())
