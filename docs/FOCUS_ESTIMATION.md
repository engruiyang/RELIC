# FOCUS_ESTIMATION（Task6A）

本阶段（Task6A）只实现 **QualityGate** 与 runtime_snapshot 质量门控字段扩展，不实现完整 FI 公式和控制状态机。

## 范围说明

- ✅ 已做：质量门控（QualityGate）、SQI 初版、运行时快照质量字段。
- ❌ 未做：FocusEstimator 完整 FI 计算。
- ❌ 未做：ControlStateEstimator 完整状态判断。
- ❌ 未做：Session / JSONL / Runtime API / GameManager 业务接入。

## 关键概念

1. **SQI 仅表示信号质量门控，不等于用户专注度。**
2. `mock` calibration 仅用于 demo/debug，不允许 formal training。
3. `attention_std=0` 不视为崩溃条件；后续 FI 需要走 fallback。
4. 数据丢失（如 attention_lost / gyro_lost）不能直接解释为疲劳或心理状态变化，只表示当前信号不可可靠估计。

## Task6A 输出字段

runtime_snapshot 中新增/确认：

- `sqi`
- `quality_state`（ok / warning / error）
- `quality_reasons`
- `calibration_usable`
- `formal_training_allowed`
- `signal_reliable`
- `estimation_allowed`
