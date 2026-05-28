# TASK26 Render Model Contract（TASK26E-0）

## 为什么需要 render model
- page config 面向配置作者，字段较多且语义偏声明式。
- QML 渲染层更适合消费“已展开坐标/尺寸”的结构化模型。
- render model 作为中间层，有助于在不改 legacy GUI 的前提下推进卡片化。

## 为什么不让 QML 直接解析复杂 page JSON
- 避免在 QML 内承担复杂结构校验与坐标计算逻辑。
- 降低 QML 侧动态解析风险，保持渲染层职责单一。
- 有利于 CI 在 Python 侧先做静态校验与编译。

## page config 与 render model 的区别
- page config：声明 card/widget 的配置、网格位置、动作与字段来源。
- render model：预编译得到可直接渲染的数据，包括 `x/y/width/height` 和规整后的 widget 字段。

## grid 坐标转换规则
- 输入：`columns/rows/gap/padding/page_width/page_height`。
- 先算 cell 尺寸，再按 `(col,row,col_span,row_span)` 计算 card 的 `x/y/width/height`。
- `col/row` 从 1 开始，超出网格边界直接报错。

## source / action_id 策略
- `source` 与 `action_id` 在 render model 中只保留原始值。
- 本阶段不执行 source，不解析表达式，不调用动作。

## 运行边界
- render model 仅用于离线原型与测试，不接入真实 GUI 运行流程。
- TASK26E-0 不修改 `HomePage.qml`，也不改 `MinimalGui` 或其它 legacy page。

## 后续阶段
- TASK26E-1 再考虑让 QML 预览层读取 render model。
- 本阶段不实现 `CardHost.qml` / `DesktopHost.qml` / `WidgetRenderer.qml`。

## Home card slots（TASK26E-2）
- E-2 新增 Home card slots 的目标是验证“render model -> 固定 UI 槽位摘要”的映射可视化。
- 当前采用固定 4 槽位（对应 home demo 的前 4 张卡片），便于稳定验证与测试。
- 预览组件不使用 `Repeater`，避免在本阶段引入额外动态渲染复杂度。
- 该方案仍不接管 `HomePage`，仅在 `DeveloperLab` 做隔离验证。
- E-2 是通向未来 `CardHost` 的中间阶段：先验证槽位映射，再推进动态渲染。
- 预计 E-3 才考虑通过 Python/bridge 传入动态 slots（仍需保持安全边界）。

## E-3 受控注入 payload
- E-3 的目标是把 slots 数据整理为“扁平注入属性”，便于 QML 预览组件直接绑定。
- 采用扁平字段（如 `slot1_card_id`、`slot1_rect_text`）是为了减少 QML 侧结构解析复杂度。
- 仍禁止 QML 直接读取 JSON 文件，避免引入文件 I/O 与解析逻辑。
- 仍不使用 `Repeater`，保持固定 4 槽位结构，确保可预测与可测试。
- E-3 只是未来 `CardHost` 的过渡层，不替代 `CardHost`。
- 未来 E-4 可考虑由 Python/bridge 提供受控 render model 属性注入，但仍需 checker 先行。

## E-3B 字段一致性合同检查
- E-3B 的目标是确保 Python 生成的 injection payload 字段，与 `HomeCardSlotsPreview.qml` 的属性定义保持一致。
- Python 侧字段使用 snake_case（如 `slot1_card_id`），QML 侧属性使用 camelCase（如 `slot1CardId`）。
- 必须维持一一映射：
  - `slotN_card_id` -> `slotNCardId`
  - `slotN_card_type` -> `slotNCardType`
  - `slotN_rect_text` -> `slotNRectText`
  - `slotN_action_ids_text` -> `slotNActionIdsText`
  - `slotN_source_roots_text` -> `slotNSourceRootsText`
  - `slotN_first_widget_labels_text` -> `slotNFirstWidgetLabelsText`
- 在 E-4 前先建立自动一致性检查，可降低字段漂移导致的 UI 绑定失效风险。
- 当前仍不接 bridge、不接 HomePage、不实现真实 CardHost，仅做 DeveloperLab 原型校验。

## E-3C Unified Injection Contract Gate
- E-3C 的目标是把 TASK26 关键合同检查统一到 `tools/check_task26_contracts.py`，避免分散脚本漏检。
- 该工具负责一次性检查：example JSON 可解析/脚本风险、pipeline coverage（默认与 strict）、home render model、home slots、home slots injection payload、payload↔QML property 映射一致性、DeveloperLab 显式传参关键字段。
- `--strict` 用于开启严格 coverage 规则，确保 mandatory pipeline 的覆盖要求按 strict 方式验证。
- `--show-diff` 用于输出 Python payload 字段、QML property、DeveloperLab 传参三者差异摘要，便于定位合同漂移。
- 在 E-4 前先建立 gate 可显著降低“字段改动后 UI 静默失效”的风险。
- 当前仍不接 bridge，仍不接 HomePage，仍不实现真实 CardHost。

## E-4A renderResources / bridge 受控输出
- E-4A 的目标是把 Home slots payload 暴露到 Python 数据层（facade/bridge），而不是直接接入页面渲染。
- `renderResourcesJson` 可包含 `task26_home_slots_payload`、`task26_home_slots_status`、`task26_home_slots_source`。
- QML 仍不读取文件系统 JSON；本阶段只保证 bridge 可读，不要求 QML 消费。
- source/action 仍不执行；不改变 command/action 执行链路。
- E-4A 与 E-4B 边界：E-4A 只提供数据，E-4B 才考虑 DeveloperLab 受控消费 bridge 属性。

## E-4B DeveloperLab 消费 renderResources
- E-4B 的目标是让 `DeveloperLabPage.qml` 从 bridge/facade 已暴露的 render resources 中读取 `task26_home_slots_payload`，再注入 `HomeCardSlotsPreview`。
- QML 不读取文件系统 JSON；DeveloperLab 只消费已经由 Python/facade/bridge 提供的 `renderResourcesObj`。
- HomePage / TrainingPage 仍不接入，legacy fallback 不受影响。
- `source` / `action_id` 仍只作为展示字段传递，不执行 source，不调用 action。
- E-4B 与未来 E-5 的边界：E-4B 只在 DeveloperLab 预览消费；如果后续进入 HomePage 试点，必须继续保留 legacy fallback。

## TASK26F-0A Training render model prototype
- TASK26F-0A extends the offline render-model prototype from Home to Training by adding `training_page.desktop_demo.json` and Python helpers that compile it into `training_desktop_render_model.example.json`.
- Training is higher risk than Home because it contains safety controls (`live.safe_stop`), training lifecycle actions (`session.start` / `session.stop`), readiness gates, calibration state, runtime freshness, game HUD state, and the existing `GameCanvas` event/render path.
- This phase is intentionally limited to audit + config + render model generation. It does not modify `TrainingPage.qml`, `HomePage.qml`, `MinimalGui.qml`, or any runtime training flow.
- The Training prototype does not connect `GameCanvas`; it only declares a locked `game_canvas_card` placeholder so the future migration has an explicit slot.
- `source` and `action_id` values remain declarative in JSON/render model. Python validates and copies them, but does not execute sources and does not invoke actions.
- Future Training migration phases must keep a legacy fallback path until the desktop/card path is fully validated under live and non-live modes.
- `GameCanvas` must be migrated separately as a dedicated `ConfigGameWidget` or `GameCanvasCard`; TASK26F-0A does not implement either component.
- `live.safe_stop` remains covered through the existing native whitelist / facade path and must stay globally accessible if any future Training desktop UI is introduced.
