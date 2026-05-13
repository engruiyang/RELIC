# TASK6B Calibration

目标：基于用户**本地** JSONL + frames.csv 标注数据，对 Task6B 参数做监督式校准，输出 `config/task6b_calibrated.yaml`（或自定义路径）。

> 注意：Codex 无法访问你的本地 `logs/task6b/`、`labels/task6b/` 与 live bridge。真实验收必须你本地执行。

## 数据路径（本地）
- `logs/task6b/task6b_live_TEST_*.jsonl`
- `labels/task6b/task6b_live_TEST_*.frames.csv`

## evaluate / tune / calibrate 区别
- `evaluate_task6b`：单次评测与误判导出。
- `tune_task6b`：候选参数搜索与候选报告。
- `calibrate_task6b`：对比 base 与 best，产出 calibrated config + calibration report + best 误判 CSV。

## 为什么不覆盖 config/task6b.yaml
`task6b.yaml` 作为稳定基线保留；校准结果输出到新文件，避免误覆盖与回滚困难。

## 生成 calibrated config
运行 `python -m ui_cli.calibrate_task6b ... --out-config config/task6b_calibrated.yaml`。

## accepted=false 含义
表示候选未达到最低门槛（例如 hard_rule_violation、false_high_focus、unreliable_miss_rate、session 覆盖等约束）。

## 查看 gyro_motion_diagnosis
查看 `reports/task6b_calibration_report.json` 中 `gyro_motion_diagnosis` 字段。

## 用于后续 live/game pipeline
在本地确认 `accepted=true` 后，再在后续 pipeline 中以 calibrated config 进行 A/B 验证。

## 本地命令
详见本任务回复中的“用户本地应运行命令”。
