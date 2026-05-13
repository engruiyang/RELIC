# COMMANDS

> Pre-Task8 curated command list. Grouped by workflow. Includes Bash + Windows PowerShell examples.

## 1) Task6B live data recording

### Bash
```bash
bash scripts/task6b_record.sh live TEST_USER 180 real_trial
```

### PowerShell
```powershell
bash scripts/task6b_record.sh live TEST_USER 180 real_trial
```

## 2) Task6B frame labeling

- Edit generated CSV under `labels/task6b/*.frames.csv` after recording.
- Recording outputs are typically in `logs/task6b/*.jsonl` and `labels/task6b/`.

## 3) Task6B evaluation

### Bash
```bash
python -m ui_cli.evaluate_task6b --input "logs/task6b/*.jsonl" --labels "labels/task6b/*.frames.csv" --config config/task6b.yaml --out reports/task6b_eval.json
# or
bash scripts/task6b_eval.sh
```

### PowerShell
```powershell
python -m ui_cli.evaluate_task6b --input "logs/task6b/*.jsonl" --labels "labels/task6b/*.frames.csv" --config config/task6b.yaml --out reports/task6b_eval.json
# or
bash scripts/task6b_eval.sh
```

## 4) Task6B tuning

### Bash
```bash
python -m ui_cli.tune_task6b --input "logs/task6b/*.jsonl" --labels "labels/task6b/*.frames.csv" --base-config config/task6b.yaml --trials 300 --method random --seed 42 --out config/task6b_tuned_candidates.json --report reports/task6b_tune_report.json
# or
bash scripts/task6b_tune.sh
```

### PowerShell
```powershell
python -m ui_cli.tune_task6b --input "logs/task6b/*.jsonl" --labels "labels/task6b/*.frames.csv" --base-config config/task6b.yaml --trials 300 --method random --seed 42 --out config/task6b_tuned_candidates.json --report reports/task6b_tune_report.json
# or
bash scripts/task6b_tune.sh
```

## 5) Runtime contract tests

### Bash
```bash
pytest -q tests/test_runtime_contract.py
```

### PowerShell
```powershell
pytest -q tests/test_runtime_contract.py
```

## 6) Session debug

### Bash
```bash
python -m ui_cli.run_session_debug --mode demo --duration-sec 1 --user-id demo_user --db-path data/relic_task7b.db
```

### PowerShell
```powershell
python -m ui_cli.run_session_debug --mode demo --duration-sec 1 --user-id demo_user --db-path data/relic_task7b.db
```

## 7) Session query

### Bash
```bash
python -m ui_cli.run_session_debug --list-sessions --db-path data/relic_task7b.db
python -m ui_cli.run_session_debug --show-session <SESSION_ID> --db-path data/relic_task7b.db
python -m ui_cli.run_session_debug --show-log-path <SESSION_ID> --db-path data/relic_task7b.db
```

### PowerShell
```powershell
python -m ui_cli.run_session_debug --list-sessions --db-path data/relic_task7b.db
python -m ui_cli.run_session_debug --show-session <SESSION_ID> --db-path data/relic_task7b.db
python -m ui_cli.run_session_debug --show-log-path <SESSION_ID> --db-path data/relic_task7b.db
```

## 8) Regression suite (Pre-Task8 gate)

### Bash
```bash
pytest -q tests/test_runtime_contract.py tests/test_session_manager.py tests/test_task6_focus_estimator.py tests/test_task6_quality_gate.py tests/test_run_core_debug_user_context.py tests/test_calibration_manager.py tests/test_calibration_cli_management.py
```

### PowerShell
```powershell
pytest -q tests/test_runtime_contract.py tests/test_session_manager.py tests/test_task6_focus_estimator.py tests/test_task6_quality_gate.py tests/test_run_core_debug_user_context.py tests/test_calibration_manager.py tests/test_calibration_cli_management.py
```
