# TASK6B Simple Tuning

## 步骤 1：录制 5 段数据

```bash
bash scripts/task6b_record.sh live TEST 60 startup
bash scripts/task6b_record.sh live TEST 90 distracted
bash scripts/task6b_record.sh live TEST 90 stable_focus
bash scripts/task6b_record.sh live TEST 120 distracted_to_focus
bash scripts/task6b_record.sh live TEST 90 gyro_motion
```

## 步骤 2：编辑 `labels/task6b/*.yaml`

只改 `label`、`start`、`end`、`note`。不确定就标 `IGNORE`。

## 步骤 3：评测

```bash
bash scripts/task6b_eval.sh
```

## 步骤 4：调参

```bash
bash scripts/task6b_tune.sh
```

## 步骤 5：查看结果

- `reports/task6b_eval.json`
- `reports/task6b_tune_report.json`
- `config/task6b_tuned_candidates.json`

## 步骤 6：人工选择候选配置

不要自动覆盖 `config/task6b.yaml`。满意后手动复制到 `config/task6b.yaml` 或 `config/task6b_selected.yaml`。
