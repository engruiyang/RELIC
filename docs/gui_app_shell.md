# TASK23 AppShell

TASK23 重建专业 AppShell，保持 bridge-only：QML 仅使用 guiBridge.appState / runtimeSnapshot / sessionState / gameHudJson / controlManifestJson / controlStateJson，并通过 guiBridge.invokeAction 调用动作。

## 页面结构
- Home
- User/Profile
- Calibration
- Training
- Report
- Diagnostics (Developer Diagnostics Console)

## 关键边界
- 不恢复 GameCanvas（留到 TASK24）。
- Training 仅展示 HUD 摘要。
- 报告增强和完整 viewer 留到 TASK25。
- QML 不访问底层模块，不写 GameEvent，不判断命中。

## 全局菜单与控制面板
- 导航：Home/User/Calibration/Training/Report/Diagnostics
- 动作：Refresh/Load Current User/Show Profile/Calibration Status/Start Session/Stop Session/Safe Stop/Reconnect/Game Status/Quit

## Home Next Action
根据已有字段给轻提示：无用户->加载用户；无 profile->User；无可用校准->Calibration；live 断开->Reconnect；质量差->Diagnostics；可训练->Training。

## 美工接入骨架（文本）
- manifest: `assets/manifest.json`
- theme: `assets/themes/default/theme.json`
- layout: `assets/layouts/*_page.json`, `assets/layouts/app_shell.json`

美工可改背景、图标 key、色彩 token、按钮样式、线框；不可改 action_id/page_id、GuiBridge 调用链、Runtime API、GameEvent 协议、SQI/FI/control_state 语义。
