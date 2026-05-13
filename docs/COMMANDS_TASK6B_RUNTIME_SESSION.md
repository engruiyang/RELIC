# COMMANDS_TASK6B_RUNTIME_SESSION

## 1. Task6B live 数据录制
```bash
bash scripts/task6b_record.sh live TEST 180 real_trial
```
PowerShell:
```powershell
bash scripts/task6b_record.sh live TEST 180 real_trial
```

## 2. Task6B 帧级标注
- 标注文件位置：`labels/task6b/*.frames.csv`
- 录制元数据：`labels/task6b/*.yaml`

## 3. Task6B 评测
```bash
python -m ui_cli.evaluate_task6b --input "logs/task6b/*.jsonl" --labels "labels/task6b/*.frames.csv" --config config/task6b.yaml --out reports/task6b_eval.json
```
PowerShell:
```powershell
python -m ui_cli.evaluate_task6b --input 'logs/task6b/*.jsonl' --labels 'labels/task6b/*.frames.csv' --config config/task6b.yaml --out reports/task6b_eval.json
```

## 4. Task6B 调参
```bash
python -m ui_cli.tune_task6b --input "logs/task6b/*.jsonl" --labels "labels/task6b/*.frames.csv" --base-config config/task6b.yaml --trials 300 --method random --seed 42 --out config/task6b_tuned_candidates.json --report reports/task6b_tune_report.json
```
PowerShell:
```powershell
python -m ui_cli.tune_task6b --input 'logs/task6b/*.jsonl' --labels 'labels/task6b/*.frames.csv' --base-config config/task6b.yaml --trials 300 --method random --seed 42 --out config/task6b_tuned_candidates.json --report reports/task6b_tune_report.json
```

## 5. Runtime 契约测试
```bash
pytest -q tests/test_runtime_contract.py
```

## 6. Session debug
```bash
python -m ui_cli.run_session_debug --mode demo --duration-sec 1 --user-id demo_user --db-path data/relic_task7b_cleanup.db
```
PowerShell:
```powershell
python -m ui_cli.run_session_debug --mode demo --duration-sec 1 --user-id demo_user --db-path data/relic_task7b_cleanup.db
```

## 7. Session list
```bash
python -m ui_cli.run_session_debug --list-sessions --db-path data/relic_task7b_cleanup.db
```

## 8. Session show
```bash
python -m ui_cli.run_session_debug --show-session <SESSION_ID> --db-path data/relic_task7b_cleanup.db
```

## 9. 回归测试
```bash
pytest -q tests/test_runtime_contract.py tests/test_session_manager.py tests/test_task6_focus_estimator.py tests/test_task6_quality_gate.py tests/test_run_core_debug_user_context.py tests/test_calibration_manager.py tests/test_calibration_cli_management.py
```

## 10. 路径说明
- Task6B JSONL：`logs/task6b/`
- Task6B labels：`labels/task6b/`
- Task6B reports：`reports/`
- 正式 session 日志：`logs/sessions/`

> `logs/task6b/` 只用于 Task6B 数据采集、标注和调参。  
> `logs/sessions/` 只用于正式训练 session 日志。两者不得混用。
