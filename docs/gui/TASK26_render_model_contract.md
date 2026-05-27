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
