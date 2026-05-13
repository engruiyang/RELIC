# Task6B Grid Calibration

本工具使用 **deterministic grid search**，参数候选来自本地标注数据分布（非脑补固定参数）。

- 不覆盖 `config/task6b.yaml`。
- 结果输出到 `config/task6b_grid_calibrated.yaml`（或自定义路径）。
- Codex 无法读取你的本地真实数据，真实结果必须在本地运行验证。

关键查看项：
- `active_grid`
- `top_candidates`
- `accepted`（true/false）

命令：
```bash
python -m ui_cli.grid_calibrate_task6b \
  --input "logs/task6b/task6b_live_TEST_*.jsonl" \
  --labels "labels/task6b/task6b_live_TEST_*.frames.csv" \
  --base-config config/task6b.yaml \
  --out-config config/task6b_grid_calibrated.yaml \
  --report reports/task6b_grid_calibration_report.json \
  --misclassified-out reports/task6b_grid_calibration_misclassified.csv \
  --top-k 20 \
  --cv-mode leave-one-session-out
```
