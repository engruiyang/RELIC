# TASK26 Checker Contract（TASK26C-2）

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

## strict 与 non-strict coverage
- `non-strict`（默认）：mandatory pipeline 的 `required_cards/required_fields/required_buttons` 各自“至少命中一个”即可。
- `strict`：mandatory pipeline 的 required 项需要全部命中（空 required 列表则跳过该类）。

## 为什么默认仍使用 non-strict
- TASK26 仍处于迁移早期，配置还在演进；默认 non-strict 可降低早期阻塞。
- 但在 TASK26D 前，推荐 `--strict` 也能通过，确保配置质量。

## source root whitelist
- 仅允许以下 source 根对象：
  - `appState`
  - `runtimeSnapshot`
  - `sessionState`
  - `controlState`
  - `controlStateJson`
  - `gameHud`
  - `gameHudJson`
  - `gameView`
  - `gameViewJson`
  - `renderResources`
  - `renderResourcesJson`
- 禁止 source 中出现脚本或注入倾向 token（如 `()`, `;`, `=`, `javascript:`, `eval` 等）。

## asset_id 校验策略
- checker 会收集 example JSON 中 asset_id，并与 `assets/manifest.json` / `assets/packs/default/pack.json` 的已知资产集合做交叉校验。
- 允许临时前缀：`placeholder_` / `preview_`。

## placeholder / preview 规则
- 迁移早期允许 `placeholder_` / `preview_` 资产占位通过。
- 在真实页面接入前，应逐步减少占位资产并替换为 manifest/pack 正式资产。

## TASK26D 前边界
- 在 TASK26D 前，不接入真实页面，不替换 legacy GUI。
- checker 仅校验 example JSON 与配置约束。

## JSON 安全约束
- JSON 不允许脚本逻辑，不允许 `function/eval/script/javascript:/=>/onClicked/Qt.callLater` 等可执行倾向内容。
