# TASK25 当前进度反向整理审计（面向 TASK26）

> 审计时间：2026-05-27（UTC）
> 范围：`ui_qml/`、`assets/`、`gui/`、`game/`、`games/`、`tests/`、`docs/`
> 约束确认：本次仅新增文档，不改动 QML/Python/JSON 功能实现、不改 action_id、不改 bridge-only 架构。

## 1. 当前 TASK25 已完成内容

### 1.1 页面读取设计包覆盖情况
- 已接入 `renderResourcesObj.page_styles` 的页面：`HomePage`、`UserPage`、`CalibrationPage`、`TrainingPage`、`ReportPage`、`DiagnosticsPage`、`DeveloperLabPage`。
- Shell 级背景使用 `app_shell`。
- 结论：页面级 design pack 读取已全页贯通（8 页面 + shell）。

### 1.2 组件读取 theme / layout / component json 情况
已实现：
- `DesignBackground.qml`：读取 layered 背景、asset_key、gradient/overlay 与 theme fallback。
- `DesignButton.qml`：读取 `normal/pressed/disabled` 样式与 asset_key。
- `DesignPanel.qml`：读取 panel/frame 与资源槽位。
- `PageHeader.qml`：读取 header 样式与 decorator_asset_key。
- `PageFeedbackPanel.qml`：读取反馈样式并按 status 选资源槽位。
- `DesignMetricCard.qml`：读取 metric 样式（尺寸/颜色/字号）。
- `GameCanvas.qml`：读取 `game_styles.trace_lock` + `effect_styles.trace_lock`。

边界：
- `assets/layouts/*.json` 对主页面布局不是主驱动来源，当前仍以 QML Anchors/Row/Column 为主。

### 1.3 已支持参数化视觉项
- 页面背景：色/图/渐变/overlay/opacity/fit/position。
- 面板/按钮/反馈/页头：背景、边框、半径、透明度、文本色、装饰资源、按钮三态。
- GameCanvas：canvas 背景与边框、target 样式、timer/progress 样式、effect 参数。

### 1.4 GameCanvas 与 TraceLock 素材包
- 结论：**已读取**。
- `trace_lock.json` 提供 asset_key；`GameCanvas.qml` 通过 `renderResourcesObj.assets` 解析 URL，并保留 fallback 图形/颜色。

### 1.5 动效/粒子/光效参数化
- 结论：**已存在基础参数化**。
- `trace_lock_effects.json` 已定义 `duration_ms/particle_count/color/glow/radius/scale/opacity/type` 等，`GameCanvas.qml` 已消费。

### 1.6 handoff / manifest 检查
- 结论：**已具备规则 + 校验 + 测试**。
- `assets/manifest.json` + `assets/packs/default/pack.json` 声明 slot/handoff。
- `core/resource_managers.py` 有 `validate_design_pack_asset_handoff()`。
- `tests/test_task25e_asset_handoff_contract.py` 覆盖校验链路。

## 2. 当前 GUI 配置能力边界

### 2.1 美工可通过 JSON 修改
- 页面背景与页面皮肤：`assets/packs/default/pages/*.json`
- 组件皮肤：`assets/packs/default/components/*.json`
- TraceLock 画布与目标样式：`assets/packs/default/games/trace_lock.json`
- 特效视觉参数：`assets/packs/default/effects/trace_lock_effects.json`
- 资源槽位 URL 映射：`assets/manifest.json`

### 2.2 仍写死在 QML
- 页面标题/副标题、绝大多数按钮文案。
- 页面 section 结构与顺序。
- 动作按钮集合与布局（非 JSON 动态渲染）。
- 多数字段绑定关系（展示哪些状态字段）。
- 导航按钮顺序与跳转。

### 2.3 仍写死在 Python
- `GuiBridge` 暴露的 Property 字段集合。
- render resource bundle 结构与默认 pack 读取流程。
- 页命令清单协议结构。

### 2.4 当前不可配置或部分不可配置
- 按钮 action_id 绑定语义（仍在 QML 内固定）。
- 状态字段编排与文案。
- 统一卡片 schema（尚未建立）。
- 局部尺寸/间距虽可配，但不是“全控件全字段可配”。

## 3. 当前 GUI 页面结构

### HomePage.qml
- 组件：`DesignBackground` / `PageHeader` / `DesignPanel` / `DesignButton` / `PageFeedbackPanel`
- JSON：`home_page` + components + theme
- guiBridge 字段：`controlStateObj`、`runtimeObj`、`commandSummary`
- action_id：含 `app.refresh_now` 与首页动作面板动作
- 卡片化适配：高

### UserPage.qml
- 组件：`DesignBackground` / `PageHeader` / `DesignPanel` / `DesignButton` / `PageFeedbackPanel`
- JSON：`user_page` + components
- guiBridge：`invokeAction` + `appStateObj/controlStateObj`
- action_id：`user.list`/`user.create`/`user.load`/`user.load_current` 等
- 卡片化适配：高

### CalibrationPage.qml
- 组件：同上
- JSON：`calibration_page` + components
- guiBridge：`invokeAction` + `controlStateObj`
- action_id：`calibration.status/list/latest/show/bind/start/poll/cancel`
- 卡片化适配：高

### TrainingPage.qml
- 组件：`DesignBackground` / `PageHeader` / `DesignPanel` / `DesignButton` / `DesignMetricCard` / `GameCanvas` / `PageFeedbackPanel`
- JSON：`training_page` + components + `games/trace_lock.json` + `effects/trace_lock_effects.json`
- guiBridge：`appStateObj/controlStateObj/runtimeObj/gameHudObj/gameViewObj/renderResourcesObj` + `invokeAction/sendCommand/sendEvent`
- action_id：`training.readiness`、`session.start` 等训练动作
- 卡片化适配：很高

### ReportPage.qml
- 组件：`DesignBackground` / `PageHeader` / `DesignPanel` / `DesignButton` / `PageFeedbackPanel`
- JSON：`report_page` + components
- guiBridge：`invokeAction` + 会话/报告状态
- action_id：`report.show`、`report.export` 等
- 卡片化适配：高

### DiagnosticsPage.qml
- 组件：`DesignBackground` / `PageHeader` / `DesignPanel` / `DesignButton` / `PageFeedbackPanel`
- JSON：`diagnostics_page` + components
- guiBridge：runtime/control/session/game HUD 综合字段
- action_id：诊断/刷新/安全停类动作
- 卡片化适配：中高

### DeveloperLabPage.qml
- 组件：`DesignBackground` / `PageHeader` / `DesignPanel` / `DesignButton` / `PageFeedbackPanel`
- JSON：`developer_lab_page` + components
- guiBridge：命令目录呈现
- action_id：以 copy_only/manual 命令元数据为主
- 卡片化适配：中

### MinimalGui.qml
- 结构：顶部状态条 + 左导航 + 右 page host
- JSON：`app_shell` + page/component style map
- guiBridge 字段：`appState/runtimeSnapshot/sessionState/gameHudJson/gameViewJson/controlStateJson/pageCommandManifestJson/renderResourcesJson`
- action_id：`app.refresh_now`、`live.safe_stop` 等
- 卡片化适配：高（保持 shell，内容区改 CardHost）

## 4. 当前组件结构

### DesignBackground.qml
- 已支持：layered/color/image/gradient/overlay/asset_key/theme path
- 未支持：复杂背景动画与高级混合
- TASK26 基础：高

### DesignButton.qml
- 已支持：三态样式 + asset_key 贴图
- 未支持：icon+text 模板、多语义状态（loading/checked/danger）
- TASK26 基础：高

### DesignMetricCard.qml
- 已支持：尺寸、边框、颜色、label/value 字号
- 未支持：多字段模板/趋势图/单位格式策略
- TASK26 基础：高

### PageHeader.qml
- 已支持：title/subtitle 样式、decorator asset
- 未支持：标题文案 JSON 化、右侧操作槽
- TASK26 基础：中高

### PageFeedbackPanel.qml
- 已支持：状态图标槽位映射、样式参数
- 未支持：反馈字段 schema 化（字段集合固定）
- TASK26 基础：高

### GameCanvas.qml
- 已支持：TraceLock 视觉 + effect 参数 + asset fallback
- 未支持：插件化 effect 引擎与完整粒子系统
- TASK26 基础：高（可作为 GameCard 渲染核）

### 其他组件
- `DesignPanel.qml`：通用容器样式化，适合作为 Card 容器基底。

## 5. 当前测试情况

### 5.1 GUI 相关测试
- 加载/结构：`test_gui_qml_loads.py`、`test_gui_real_pages.py`、`test_gui_page_shell.py`
- 可见结构：`test_gui_user_page_visible_structure.py`、`test_gui_calibration_page_visible_structure.py`、`test_gui_training_page_visible_structure.py`、`test_gui_report_page_visible_structure.py`
- 行为动作：`test_gui_page_actions_runtime.py`、`test_gui_page_action_panels.py`、`test_gui_calibration_page_actions.py`、`test_gui_report_page_actions.py`、`test_gui_user_page_actions.py`
- 协议桥接：`test_gui_bridge.py`、`test_gui_protocol.py`、`test_gui_command_dispatcher.py`、`test_gui_command_registry.py`

### 5.2 资产检查相关测试
- `test_task25e_asset_handoff_contract.py`
- `test_design_pack_contract.py`
- `test_gui_task25_design_pack_consumption.py`
- `test_gui_task25_game_canvas_asset_pack.py`
- `test_task25_visual_asset_pipelines.py`、`test_trace_lock_visual_contract.py`、`test_gui_art_asset_contract.py`

### 5.3 QML 禁用结构检查
- `test_gui_qml_style_safety.py`：检查 inline object chain 风险（`GameCanvas.qml` 特例）+ TrainingPage 前 80 行 banned token。
- 当前未看到单独针对 `Loader/Repeater/Timer/subprocess` 的统一测试禁令文件。

### 5.4 TASK26 动态卡片化后的测试调整
需调整：
- 页面可见结构测试（从静态控件断言改为 schema 渲染断言）。
- 动作面板按钮数量/顺序断言（改为配置驱动断言）。

不能破坏：
- bridge-only 协议测试。
- action_id 合同测试。
- design pack / asset_handoff 契约测试。
- GameCanvas 与 TraceLock 视觉契约测试。

## 6. 当前风险点
1. 页面结构仍手写，配置化深度不足。
2. Qt 原生控件能力与风格一致性仍可能受限。
3. 多页面字段重复，后续维护易漂移。
4. 状态展示逻辑分散在各页。
5. `layout json` 与 QML 绑定不完整。
6. 美工改“信息结构”仍需懂 QML。

## 7. TASK26 建议路线

- **TASK26A**：定义卡片 schema（card_id/type/title/fields/actions/layout/bindings/visibility）。
- **TASK26B**：新增 `DesignCard` / `CardHost` / `ButtonCard` / `MetricCard` 的配置读取。
- **TASK26C**：Home + Training 先做卡片化试点。
- **TASK26D**：扩展到 Calibration / Report / Diagnostics。
- **TASK26E**：按钮、字段、动作、显示信息全配置化（保留现有 action_id）。
- **TASK26F**：补 schema 校验与视觉回归测试。

## 修改文件列表
- `docs/gui/TASK25_current_status_audit.md`（新增）

## 建议测试命令
- `pytest -q tests/test_gui_qml_style_safety.py`
- `pytest -q tests/test_gui_task25_design_pack_consumption.py tests/test_gui_task25_game_canvas_asset_pack.py`
- `pytest -q tests/test_task25e_asset_handoff_contract.py tests/test_design_pack_contract.py`
- `pytest -q tests/test_gui_real_pages.py tests/test_gui_page_action_panels.py tests/test_gui_page_actions_runtime.py`
