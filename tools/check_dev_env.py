from __future__ import annotations
import importlib
import sys
from pathlib import Path

REQUIRED_FILES = [
    "tests/test_data_center_semantics.py",
    "tests/test_mock_modes_quality.py",
    "ui_qml/MinimalGui.qml",
]


def main() -> int:
    errors: list[str] = []
    for f in REQUIRED_FILES:
        if not Path(f).exists():
            errors.append(f"missing file: {f}")

    for mod in ["pytest", "PySide6"]:
        try:
            importlib.import_module(mod)
        except Exception as exc:
            errors.append(f"cannot import {mod}: {exc}")

    if errors:
        print("Dev environment check FAILED:")
        for e in errors:
            print(f"- {e}")
        return 1

    print("Dev environment OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
