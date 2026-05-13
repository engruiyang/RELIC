# Task6B Grid Calibration (Staged Grid)

当前推荐主路径：`--optimizer staged_grid --search-mode staged`。

三阶段：
1. Stage1: UNRELIABLE gate 校准。
2. Stage2: 可靠帧上的 FI 分类校准。
3. Stage3: 转场响应（distracted_to_focus）校准。

相比全参数混搜，staged 把 gate/FI/transition 解耦，减少互相干扰。

查看报告：
- `stage1_gate_search`
- `stage2_fi_search`
- `stage3_transition_search`
- `failed_checks` / `reject_reasons`
- `accepted`

Codex 无法访问你的真实本地数据；真实结果请在本地执行并验收。

```bash
python -m ui_cli.grid_calibrate_task6b \
  --optimizer staged_grid \
  --search-mode staged \
  --input "logs/task6b/task6b_live_TEST_*.jsonl" \
  --labels "labels/task6b/task6b_live_TEST_*.frames.csv" \
  --base-config config/task6b.yaml \
  --out-config config/task6b_grid_calibrated.yaml \
  --report reports/task6b_grid_calibration_report.json \
  --misclassified-out reports/task6b_grid_calibration_misclassified.csv \
  --stage1-max-combinations 20000 \
  --stage2-max-combinations 30000 \
  --stage3-max-combinations 30000 \
  --batch-size 1000 \
  --max-stored-candidates 300 \
  --n-jobs 1 \
  --candidate-log reports/task6b_grid_candidates.jsonl
```
