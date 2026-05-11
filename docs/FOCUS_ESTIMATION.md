# FOCUS_ESTIMATION（Task6A）

Task6A 先实现 **QualityGate**；Task6B 在此基础上实现 FocusEstimator、FI 初版与 ControlStateEstimator。

## 范围说明

- ✅ 已做：质量门控（QualityGate）、SQI 初版、运行时快照质量字段。
- ✅ 已做（Task6B 初版）：FocusEstimator / FI raw+smoothed / ControlStateEstimator（规则版，无 ML）。
- ❌ 未做：Session / JSONL / Runtime API / GameManager 业务接入。

## 关键概念

1. **SQI 仅表示信号质量门控，不等于用户专注度。**
2. `mock` calibration 仅用于 demo/debug，不允许 formal training。
3. `attention_std=0` 不视为崩溃条件；后续 FI 需要走 fallback。
4. 数据丢失（如 attention_lost / gyro_lost）不能直接解释为疲劳或心理状态变化，只表示当前信号不可可靠估计。
5. 当前版本没有 raw EEG 频带特征；`S_EEG` 实际是 calibrated platform attention score（接口名保留为 `s_eeg` 以便后续升级）。
6. FI 是训练状态指数，不是医学诊断指标。
7. `S_B` 当前固定 `neutral_default`（0.5），后续由游戏行为数据替换。
8. 本阶段不做机器学习；ML 需在 Session 数据积累后再考虑。

## Task6A 输出字段

runtime_snapshot 中新增/确认：

- `sqi`
- `quality_state`（ok / warning / error）
- `quality_reasons`
- `calibration_usable`
- `formal_training_allowed`
- `signal_reliable`
- `estimation_allowed`
- `s_eeg`
- `s_imu`
- `s_b`
- `s_b_source`
- `attention_normalization_method`
- `motion_energy`
- `fi_raw`
- `fi_smoothed`
- `fi_valid`
- `fi_confidence`
- `fi_reasons`
- `control_state`
- `control_state_reason`
- `control_state_dwell_ms`
