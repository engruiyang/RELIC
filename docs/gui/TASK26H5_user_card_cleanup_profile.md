# TASK26H-5B User 卡片清理与 Profile 弹窗真实数据

本阶段在 H-5 User 卡片输入/下拉/弹窗基础上做收束。

## 变更

- 移除 `user_actions_card`，避免和 `user_credentials_card`、`user_selector_card` 重复。
- 重新排布 User 页面卡片，保持 12×8 grid 内无重叠。
- `user.show_profile` 返回结果中附带校准状态摘要。
- Profile Popup 优先读取最近一次 action raw result，而非只读 `controlStateJson` fallback。
- Popup 增加 `Attention baseline`、`Calibration usable`、`Gyro noise RMS` 显示项。

## 边界

- 不新增旧式独立表单。
- 不改变卡片化按钮流程。
- 不重写用户后端。
- 不接动态用户列表回灌。

## 后续

下一步可继续做动态 selector：把 `user.list` 返回的真实用户列表写入 renderResources，再让 `ComboBox` 使用真实列表。
