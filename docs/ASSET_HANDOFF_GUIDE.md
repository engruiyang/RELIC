# RELIC 美术与页面设计交付规范（Headless Core 阶段）

> 本文档用于指导后续美工/UI 设计同学交付素材，**不改变当前核心设计**。
> 适用日期：2026-05-07

## 1. 交付总原则

- 逻辑层（`relic_core/`、`games/`）不直接写死素材路径、颜色、字体。
- 所有素材通过 `assets/manifest.json` 的 key 引用。
- 所有颜色/字体/尺寸 token 通过 `assets/themes/default/theme.json` 管理。
- 页面结构通过 `assets/layouts/*.json` 提供（当前可先从占位 JSON 扩展）。

---

## 2. 目录与职责

请按以下目录放置：

```text
assets/
  manifest.json                  # 资源索引（逻辑 key -> 相对路径）
  themes/
    default/theme.json           # 主题 token（颜色、字体、尺寸）
  layouts/
    main_menu.json               # 主菜单页面结构
    quick_check.json             # 快检页面结构
    game_hud.json                # 游戏 HUD 页面结构
    report.json                  # 报告页面结构
  images/
    backgrounds/                 # 背景图
    buttons/                     # 按钮图
    icons/                       # 通用图标
    games/
      fragment_lock/             # 碎片锁定游戏图
      signal_hunter/             # 信号猎手游戏图
      stabilizer/                # 稳定协议游戏图
  fonts/                         # 字体文件
  sounds/                        # 音效文件
  animations/                    # 动画序列或导出文件
```

---

## 3. manifest.json 规范

`manifest.json` 是“资源注册表”，格式为：

```json
{
  "images.logo": "images/icons/logo.png",
  "images.main_background": "images/backgrounds/main.png",
  "images.button.normal": "images/buttons/button_normal.png",
  "images.button.hover": "images/buttons/button_hover.png",
  "sounds.click": "sounds/click.wav",
  "fonts.main": "fonts/main.ttf"
}
```

### 3.1 key 命名建议

- 采用点分层级：`类别.页面或模块.用途.状态`
- 例如：
  - `images.main_menu.background`
  - `images.button.primary.normal`
  - `images.button.primary.hover`
  - `sounds.ui.confirm`
  - `sounds.game.hit`
  - `fonts.main`

### 3.2 注意事项

- value 必须是 **assets 目录下相对路径**。
- key 一旦被代码使用，改名前需同步开发。
- 可以新增 key，不建议直接删除已有 key。

---

## 4. theme.json 规范

`assets/themes/default/theme.json` 用于设计 token。

当前已存在字段：
- `name`
- `font_family`
- `colors`（颜色 token）
- `sizes`（尺寸 token）

建议扩展但保持兼容：

```json
{
  "name": "default",
  "font_family": "Microsoft YaHei UI",
  "colors": {
    "background": "#10131A",
    "panel": "#1B2130",
    "primary": "#70E0FF",
    "secondary": "#8B7CFF",
    "warning": "#FFD166",
    "danger": "#FF5C7A",
    "text": "#F5F7FA",
    "muted_text": "#A7B0C0"
  },
  "sizes": {
    "window_width": 1280,
    "window_height": 720,
    "top_bar_height": 72,
    "bottom_bar_height": 48
  }
}
```

可扩展字段示例：
- `radius`: 圆角 token
- `spacing`: 间距 token
- `shadow`: 阴影 token
- `font_size`: 字号 token

---

## 5. 页面 layout JSON 规范（建议）

当前 `assets/layouts/*.json` 仍是占位 `{}`。建议按以下结构交付页面描述：

```json
{
  "page": "main_menu",
  "version": 1,
  "canvas": {"width": 1280, "height": 720},
  "nodes": [
    {
      "id": "bg",
      "type": "image",
      "asset": "images.main_background",
      "x": 0,
      "y": 0,
      "width": 1280,
      "height": 720,
      "anchor": "top_left"
    },
    {
      "id": "start_button",
      "type": "button",
      "style": "primary",
      "text": "开始训练",
      "x": 540,
      "y": 520,
      "width": 200,
      "height": 64,
      "states": {
        "normal": "images.button.normal",
        "hover": "images.button.hover"
      }
    }
  ]
}
```

### 5.1 推荐字段

- `page`: 页面名
- `version`: 结构版本号
- `canvas`: 设计稿尺寸
- `nodes`: 组件数组
- 节点通用字段：`id/type/x/y/width/height/anchor/visible/z_index`

### 5.2 常用节点 type

- `image`
- `text`
- `button`
- `panel`
- `progress`
- `icon`

---

## 6. 可交付素材清单

### 6.1 图片（推荐 PNG / WebP）

可交付：
- 背景图（主菜单、快检、游戏、报告）
- 按钮（normal/hover/pressed/disabled）
- 图标（状态、导航、提示）
- 游戏对象图（后续三个小游戏）

放置目录：
- `assets/images/backgrounds/`
- `assets/images/buttons/`
- `assets/images/icons/`
- `assets/images/games/<game_id>/`

建议：
- UI 元素优先透明 PNG。
- 命名包含状态后缀，如 `_normal/_hover/_pressed`。

### 6.2 字体

可交付：
- 主字体、数字字体、强调字体（如有授权）

放置目录：
- `assets/fonts/`

并在 manifest 注册：
- `fonts.main`
- `fonts.number`（可选）

### 6.3 音效

可交付：
- 点击、确认、警告、命中、miss、结算提示等

放置目录：
- `assets/sounds/`

建议：
- UI 音效命名：`ui_click.wav`、`ui_confirm.wav`
- 游戏音效命名：`game_hit.wav`、`game_miss.wav`

### 6.4 动画

可交付：
- 帧序列（PNG 序列）
- 或导出资源（按后续 UI 框架能力决定）

放置目录：
- `assets/animations/`

并在 manifest 增加对应 key。

---

## 7. 交付包建议格式

建议一次交付包含：

1. `assets/` 下新增或替换的文件。
2. 更新后的 `assets/manifest.json`。
3. 更新后的 `assets/themes/default/theme.json`（若 token 有调整）。
4. 更新后的 `assets/layouts/*.json`（若页面结构有定义）。
5. 一份变更说明（Markdown）：
   - 新增了哪些 key
   - 删除/替换了哪些 key
   - 哪些页面布局字段变更

---

## 8. 与开发协作的“最小对齐清单”

每次交付前请确认：

- [ ] manifest 的 key 唯一且语义清晰。
- [ ] theme token 名称稳定，不随意改名。
- [ ] layout 节点 id 在同页面唯一。
- [ ] 实际文件路径与 manifest 一致。
- [ ] 文件名只使用英文、数字、下划线，避免空格。
- [ ] 若替换同名素材，确认尺寸变化不会破坏布局。

---

## 9. 当前阶段边界（重要）

- 当前为 Headless Core 阶段，不直接加载 QPixmap/音频对象。
- 资源系统当前只做“路径与 token 管理”。
- 正式渲染与交互由后续 `ui_pyqt/` 适配层实现。

这意味着：美术和页面可以先按本文档沉淀素材与 JSON 规范，待 UI Adapter 接入时即可直接消费。

# 给美术同学的素材交付说明（超简版）

你好！这份说明只做一件事：
**告诉你把什么素材，用什么格式，放到哪个文件夹。**

不需要懂代码。

---

## 1）你需要交付哪些素材？

你可以交付这几类：

1. 背景图
2. 按钮图（普通/悬停/按下）
3. 图标
4. 字体文件（如果有）
5. 音效（如果有）
6. 动画资源（如果有）

---

## 2）每类素材放哪里？

请按下面放：

- 背景图 → `assets/images/backgrounds/`
- 按钮图 → `assets/images/buttons/`
- 图标 → `assets/images/icons/`
- 游戏内图片：
  - 碎片锁定 → `assets/images/games/fragment_lock/`
  - 信号猎手 → `assets/images/games/signal_hunter/`
  - 稳定协议 → `assets/images/games/stabilizer/`
- 字体 → `assets/fonts/`
- 音效 → `assets/sounds/`
- 动画 → `assets/animations/`

---

## 3）推荐文件格式

- 图片：`PNG`（优先）或 `WebP`
- 字体：`TTF` 或 `OTF`
- 音效：`WAV`（优先）或 `MP3`
- 动画：PNG 序列，或你导出的常见格式（和开发确认）

---

## 4）文件命名建议（简单好记）

请用英文和下划线，不要空格，不要中文。

示例：

- `main_bg.png`
- `btn_start_normal.png`
- `btn_start_hover.png`
- `btn_start_pressed.png`
- `icon_settings.png`
- `ui_click.wav`

---

## 5）你交付时，最重要的一件事

除了素材文件，请**额外提供一个“素材清单”文本**（txt 或 md 都行）。

清单里写三列就行：

1. 文件名
2. 放置路径
3. 用途说明

示例：

- `main_bg.png` → `assets/images/backgrounds/` → 主菜单背景
- `btn_start_normal.png` → `assets/images/buttons/` → 开始按钮普通状态
- `ui_click.wav` → `assets/sounds/` → 按钮点击音效

---

## 6）如果你只想最小交付

你至少可以先给这 4 个：

1. 一个主背景图（PNG）
2. 一个按钮普通状态图（PNG）
3. 一个按钮悬停状态图（PNG）
4. 一个图标（PNG）

放到对应目录即可，后面可以慢慢补。

---

## 7）不要担心代码

你只需要按上面放素材。
代码和配置由开发处理。

如果不确定，直接把素材包和“素材清单”发给开发同学即可。（错误，开发同学根本就不会看的，看了也看不懂LOL）
