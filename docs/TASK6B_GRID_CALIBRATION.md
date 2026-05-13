# Task6B Grid Calibration v2

v2 使用 **deterministic coarse-to-fine grid search**（默认），并支持纯 grid。
参数候选来自本地标注数据分布，不使用“脑补固定参数”作为主路径。

- 不覆盖 `config/task6b.yaml`。
- 输出 `accepted / reject_reasons / weak_sessions / tradeoff_analysis`。
- `accepted=false` 不等于无提升，表示未通过验收门槛。
- 可查看：best overall、best worst-session、best transition、safest unreliable 等 tradeoff 视图。
- 可通过 `transition_session_diagnosis` 定位 `distracted_to_focus` 弱项。
- 只有 `accepted=true` 才建议进入后续 Task8C live pipeline；否则作为 experimental config。

> Codex 无法读取你的真实本地数据。真实校准结果必须在你本地运行验证。

示例：
```bash
python -m ui_cli.grid_calibrate_task6b \
  --input "logs/task6b/task6b_live_TEST_*.jsonl" \
  --labels "labels/task6b/task6b_live_TEST_*.frames.csv" \
  --base-config config/task6b.yaml \
  --out-config config/task6b_grid_calibrated.yaml \
  --report reports/task6b_grid_calibration_report.json \
  --misclassified-out reports/task6b_grid_calibration_misclassified.csv \
  --top-k 30 \
  --cv-mode leave-one-session-out \
  --search-mode coarse-to-fine \
  --max-combinations 200000 \
  --n-jobs 8 \
  --rank-by balanced
```
