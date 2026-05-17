# TASK23A2 GUI Page Architecture

- 目标：从单页大杂烩切换为真实页面组件系统。
- AppShell 职责：TopStatusBar、Navigation、PageHost、全局安全按钮（Refresh/Safe Stop/Quit/Diagnostics）。
- 页面职责：Home(User journey)/User(Profile actions)/Calibration(校准管理)/Training(训练控制)/Report(报告摘要)/Diagnostics(TASK21 诊断台)/DeveloperLab(高级命令目录)。
- 每页都拥有 Action Panel + Page Feedback Panel，命令归属随 page_id。
- 全局按钮减少：避免功能分工混乱，降低误操作。
- Command Registry 映射：读取 `pageCommandManifestJson`，每页显示本页 `Page Commands` 摘要。
- UI 表现：native=可触发 invokeAction；manual/copy_only=仅反馈+CLI reference，不执行。
- Developer Lab 不执行危险命令：避免在 GUI 内触发高风险脚本/写文件/连接链路。
- 后续：TASK23B 接 User/Calibration 真实后端；TASK23C 对齐 RuntimeSnapshot；TASK23D 优化专业页面壳。
