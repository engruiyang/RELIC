# TASK26 Checker Contract（TASK26C）

## 为什么 TASK26C 先做 Python checker
- TASK26 当前仍处于“配置与迁移前置阶段”，优先建立离线校验，能在不改运行 GUI 的前提下验证配置质量。
- Python checker 易于 CI 集成，可在设计同学提交 JSON 后快速返回错误。

## 为什么 QML 不负责 coverage 检查
- QML 负责渲染与交互，不应承担配置合规性和 pipeline 覆盖审计逻辑。
- coverage 检查属于构建期/测试期职责，Python 更适合做结构化校验与错误汇总。

## command_registry action 与 native action whitelist
- `command_registry` action：在 `gui/command_registry.py` 中登记，适合可声明的动作。
- native action whitelist：系统壳层固有动作，不一定出现在 registry 中。

## live.safe_stop 为什么先放 native whitelist
- `live.safe_stop` 当前是壳层安全动作，未作为 registry 条目统一登记。
- 因此 checker 需支持“registry + native whitelist”双来源校验。

## 当前 coverage 规则（宽松）
- 对 mandatory pipeline：`required_cards/required_fields/required_buttons` 均采用“至少命中一个”的宽松规则。
- 该规则用于 TASK26C 快速落地，避免早期配置演进被过严规则阻塞。

## 后续严格化计划
- TASK26D/E 可升级为“全部 required 项都必须覆盖”的严格模式。
- 增加字段映射真实性校验（与 guiBridge 实际字段契约联动）。
- 增加 asset_id 与 manifest/pack 的一致性约束。

## TASK26D 前边界
- 在 TASK26D 前，不接入真实页面，不替换 legacy GUI。
- checker 仅校验 example JSON 与配置约束。

## JSON 安全约束
- JSON 不允许脚本逻辑，不允许 `function/eval/script/javascript:/=>/onClicked/Qt.callLater` 等可执行倾向内容。
