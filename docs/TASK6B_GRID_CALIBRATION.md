# Task6B Grid Calibration v3 (Memory-safe Streaming)

v3 采用 memory-safe streaming search：
- 不在内存中保存全量候选或全量结果。
- 默认 `n_jobs=1`。
- Windows 上多进程可能复制内存。
- 可用 `--candidate-log` 将候选摘要逐行落盘 JSONL。
- report 仅保留 top-k 与摘要。
- `frame_predictions` 默认关闭（`--include-frame-predictions` 才开启）。

建议从 50000 combinations 起步，逐步增加；不要同时提高 `n_jobs` 与 `stage1_top_k`。

> Codex 无法访问你的真实本地数据，真实运行与验收需在本地完成。

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
  --max-combinations 50000 \
  --batch-size 1000 \
  --max-stored-candidates 300 \
  --n-jobs 1 \
  --rank-by balanced \
  --candidate-log reports/task6b_grid_candidates.jsonl
```
