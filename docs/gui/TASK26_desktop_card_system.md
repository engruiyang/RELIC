# TASK26 Desktop Card GUI System 设计草案（TASK26A）

## 1. 为什么采用“类似手机桌面”的 GUI 模型
- RELIC 是脑机训练控制台，需要在同一界面承载实时 I/O、训练控制、校准状态、游戏 HUD、报告入口和视觉包装。
- 现有固定页面结构可维护性高，但对美工与策展式布局编辑不友好。
- “桌面卡片模型”可将结构与样式解耦，便于按场景快速重排。
- 卡片模型可支持“强制模块 + 自由模块”并存，兼顾安全约束与可设计性。

## 2. Desktop 层级模型
- **Desktop**：全局容器，定义版本、模式、页面集合与系统层策略。
- **StatusBar**：顶部/底部状态常驻层，承载关键状态灯、连接态、安全入口。
- **Dock**：常驻操作入口层，承载全局动作（特别是 `live.safe_stop`）。
- **Page**：每个业务页面的逻辑容器，内部由 cards 组成。
- **Card**：页面中的可排布单元，支持 required/locked/preset/shape/style。
- **Widget**：卡片内部最小可配置单元（metric/text/button/image/hud/game 等）。
- **Wallpaper**：桌面背景层，支持颜色、图片、渐变等视觉包装。

## 3. 四类模块
- **Level 0：系统常驻层**（StatusBar / Dock / 全局安全入口）。
- **Level 1：强制 I/O 卡片**（连接、流质量、告警、安全控制）。
- **Level 2：功能入口卡片**（训练、校准、报告、诊断、用户操作）。
- **Level 3：自由装饰与扩展卡片**（说明、统计、视觉装饰、快捷入口）。

## 4. 强制模块与自由模块的区别

### 强制模块
- 可以移动。
- 可以缩放。
- 可以改颜色。
- 可以改背景。
- 可以改边框。
- 可以改形状。
- 可以折叠。
- **不能从整个 GUI 配置中消失**。

### 自由模块
- 可以添加。
- 可以删除。
- 可以换位置。
- 可以换样式。
- 可以作为装饰、说明、统计、快捷入口。

## 5. 支持的 card / widget 类型草案
- `metric`
- `text`
- `button`
- `image`
- `hud`
- `game`
- `divider`
- `spacer`
- `status_light`

## 6. 第一版支持的形状
- `rect`
- `rounded_rect`
- `pill`
- `circle`
- `cut_corner`
- `image_frame`

实现优先级建议：
- 第一优先：`rect / rounded_rect / pill / circle`。
- `cut_corner / image_frame` 第一版可先作为配置占位，或以图片边框模拟。
- 第一版不建议实现复杂 `mask`、`clip path`、SVG 动态描边。

## 7. bridge-only 边界
- QML 只渲染，不直接承载外部 I/O。
- QML 不直接访问 socket。
- QML 不直接访问数据库。
- QML 不直接绕过 `command_registry`。
- 按钮只能引用 `action_id`。
- `action_id` 必须由 `command_registry` 校验。
