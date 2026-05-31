# TASK26H-5D User Profile Baseline and Input Clear Fix

本补丁修复两个问题：

1. User 页面 profile 字段不应只依赖最近一次按钮 action 的返回结果。`GuiFacade.get_control_state()` 现在会基于当前用户读取数据库中的 profile 与 calibration summary，并把 `profile_loaded`、`last_calibration_id`、`attention_low_threshold`、`attention_high_threshold`、`attention_baseline`、`calibration_usable`、`gyro_noise_rms` 等字段稳定暴露到 `controlStateJson`。

2. Register / Login 卡片的输入框默认值不应在用户删除文本后自动恢复。`DesktopLayoutCardPreview.qml` 现在只在组件完成时初始化输入框，之后允许用户清空或修改内容。

同时，`user_credentials_card` 的说明文案和输入框标签更明确，避免用户不知道三个输入框的用途。
