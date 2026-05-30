from __future__ import annotations

import importlib.util
from pathlib import Path


REQUIRED_FILES = [
    "tests/test_data_center_semantics.py",
    "tests/test_mock_modes_quality.py",
    "ui_qml/MinimalGui.qml",
]

REQUIRED_MODULES = [
    "pytest",
    "PySide6",
]


def main() -> int:
    missing_files = [path for path in REQUIRED_FILES if not Path(path).exists()]
    missing_modules = [
        module for module in REQUIRED_MODULES
        if importlib.util.find_spec(module) is None
    ]

    if missing_files:
        print("Missing required files:")
        for path in missing_files:
            print(f"  - {path}")

    if missing_modules:
        print("Missing Python modules:")
        for module in missing_modules:
            print(f"  - {module}")

    if missing_files or missing_modules:
        return 1

    print("Dev environment OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
