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

如果不确定，直接把素材包和“素材清单”发给开发同学即可。
