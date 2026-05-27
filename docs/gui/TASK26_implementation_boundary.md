# TASK26 实施边界说明（TASK26A）

## 1. TASK26 的定位
- TASK26 是新增 **Desktop Card GUI System**，目标是提供“类似手机桌面”的可配置卡片层。
- TASK26 不删除当前 legacy GUI。
- TASK26 不直接重写 `MinimalGui.qml`。
- TASK26 不直接重写 `TrainingPage.qml`。
- TASK26 建议先以预览层形式接入 `DeveloperLab` 或 `Diagnostics`，后续再逐步迁移 `Home` / `Training`。

## 2. TASK25 与 TASK26 的关系
- TASK25 重点是视觉参数外置（theme/page/component/game/effects）。
- TASK26 重点是页面结构、卡片组合、字段绑定、按钮入口配置化。
- TASK25 的 `DesignBackground / DesignButton / DesignPanel / DesignMetricCard / PageFeedbackPanel / GameCanvas` 可作为 TASK26 的基础资源。
- TASK26 不推翻 TASK25，而是在其稳定基线上扩展“结构配置化能力”。

## 3. Legacy GUI 保留策略
- `HomePage / TrainingPage / CalibrationPage / ReportPage / DiagnosticsPage / DeveloperLabPage` 先保留。
- 新 Desktop Layer 与 legacy pages 并存，采用渐进迁移。
- 后续优先迁移 `HomePage`。
- `TrainingPage` 后迁移，因为其耦合 `GameCanvas`、session、readiness、runtime、HUD 与 `live.safe_stop` 安全控制。

## 4. Codex 工作边界
- Codex 可以：写文档、example JSON、配置说明、批量字段整理。
- Codex 不负责：核心 QML 渲染实现。
- Codex 不负责：`CardHost / DesignCard / WidgetRenderer` 的架构实现。
- Codex 不允许：自由重构 QML。
- Codex 不允许：发明 action_id。

## 5. 后续阶段概览
- **TASK26B**：人工提供核心 QML 组件。
- **TASK26C**：Python schema 与 coverage checker。
- **TASK26D**：DeveloperLab / Diagnostics 预览接入。
- **TASK26E**：首页迁移。
- **TASK26F**：训练页迁移。
- **TASK26G**：其他页面迁移。
- **TASK26H**：美工编辑指南。
- **TASK26I**：legacy fallback 策略。
