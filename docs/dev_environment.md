# Dev Environment for TASK23 GUI

## Required dependencies
- Python 3.13
- `pytest`
- `PySide6` (required for GUI/QML load tests)

Install:

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

## Required legacy tests in repo
The following files must exist in `tests/` and are required for compatibility checks:
- `tests/test_data_center_semantics.py`
- `tests/test_mock_modes_quality.py`

## Environment self-check
Run:

```bash
python tools/check_dev_env.py
```

It validates file presence and imports for `pytest` and `PySide6`.

## Recommended Windows local validation
```bash
python tools/check_dev_env.py
python -m pytest tests/test_data_center_semantics.py -vv
python -m pytest tests/test_mock_modes_quality.py -vv
python -m pytest tests/test_gui_qml_loads.py -vv
python -m pytest tests -k "gui" -vv
python -m pytest tests -vv
```

## CI / Codespaces / Codex notes
- GitHub Actions workflow: `.github/workflows/task23_gui_ci.yml`.
- PySide6 is mandatory for true GUI load coverage.
- If PySide6 is unavailable in a runtime, do **not** claim GUI load tests passed; report as skipped/unverified.

## PR summary requirements
PR summaries should include:
- `tools/check_dev_env.py` result
- `tests/test_data_center_semantics.py` result
- `tests/test_mock_modes_quality.py` result
- `tests/test_gui_qml_loads.py` result
- `pytest -k "gui"` result
