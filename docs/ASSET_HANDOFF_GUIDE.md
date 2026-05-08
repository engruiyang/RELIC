# 美术交付说明（从 0 开始，一眼看懂版）

> 旧版说明已弃用。请只看这份。

<<<<<<< codex/implement-headless-app-core-3pjlpu
你不用懂代码。
你只要照着下面做，就不会错。
=======
不用懂代码。
只要照着下面做，就不会错。(理论上)
>>>>>>> main

---

## 第 1 步：先知道你要交什么

你只需要交两部分：

### A. 素材文件（图片/字体/音效）

放到这些文件夹：

- 背景图：`assets/images/backgrounds/`
- 按钮图：`assets/images/buttons/`
- 图标：`assets/images/icons/`
- 游戏图：
  - 碎片锁定：`assets/images/games/fragment_lock/`
  - 信号猎手：`assets/images/games/signal_hunter/`
  - 稳定协议：`assets/images/games/stabilizer/`
- 字体：`assets/fonts/`
- 音效：`assets/sounds/`
- 动画：`assets/animations/`

### B. 3 个 JSON 文件（很简单，照抄模板改字就行）

1. `assets/manifest.json`（写“素材名字 -> 文件路径”）
2. `assets/themes/default/theme.json`（写颜色、字体、尺寸）
3. `assets/layouts/main_menu.json`（写页面上有什么）

---

## 第 2 步：JSON 怎么写（不会也能写）

请记住 4 条：

1. 最外层用 `{ }`
2. 每一项是 `"名字": 值`
3. 字符串必须加英文双引号 `"`（不要用中文引号）
4. 每项后面用英文逗号 `,`，最后一项不要逗号

### 正确示例

```json
{
  "name": "default",
  "width": 1280
}
```

### 错误示例（不要这样写）

```json
{
  name: "default",
  "width": 1280,
}
```

错因：
- `name` 没加双引号
- 最后一行多了逗号

---

## 第 3 步：manifest.json 怎么写（最重要）

文件位置：`assets/manifest.json`

它的作用：
**给每个素材起一个“代码名”，并告诉系统素材在哪个路径。**

直接按这个模板填：

```json
{
  "images.logo": "images/icons/logo.png",
  "images.main_background": "images/backgrounds/main_bg.png",
  "images.button.start.normal": "images/buttons/btn_start_normal.png",
  "images.button.start.hover": "images/buttons/btn_start_hover.png",
  "sounds.click": "sounds/ui_click.wav",
  "fonts.main": "fonts/main.ttf"
}
```

### 你要改哪里？

- 左边（比如 `images.logo`）是“名字”，可以按示例风格新增
- 右边是**真实文件路径**（相对 `assets/`）

例如你放了文件：
- 实际文件：`assets/images/icons/icon_help.png`

那就写：

```json
"images.icon.help": "images/icons/icon_help.png"
```

---

## 第 4 步：theme.json 怎么写

文件位置：`assets/themes/default/theme.json`

它的作用：
**统一颜色、字体、窗口大小。**

直接用这个模板：

```json
{
  "name": "default",
  "font_family": "Microsoft YaHei UI",
  "colors": {
    "background": "#10131A",
    "panel": "#1B2130",
    "primary": "#70E0FF",
    "text": "#F5F7FA"
  },
  "sizes": {
    "window_width": 1280,
    "window_height": 720,
    "top_bar_height": 72,
    "bottom_bar_height": 48
  }
}
```

说明：
- 颜色必须是 `#` 开头，比如 `#FFFFFF`
- 尺寸必须是数字，不要加单位（不要写 `1280px`）

---

## 第 5 步：layout（页面）json 怎么写

先从主菜单开始：`assets/layouts/main_menu.json`

它的作用：
**告诉系统页面上有哪些东西（背景、按钮、文字）。**

请直接从下面这个最小模板开始：

```json
{
  "page": "main_menu",
  "canvas": {
    "width": 1280,
    "height": 720
  },
  "nodes": [
    {
      "id": "bg",
      "type": "image",
      "asset": "images.main_background",
      "x": 0,
      "y": 0,
      "width": 1280,
      "height": 720
    },
    {
      "id": "btn_start",
      "type": "button",
      "text": "开始训练",
      "x": 540,
      "y": 520,
      "width": 200,
      "height": 64,
      "states": {
        "normal": "images.button.start.normal",
        "hover": "images.button.start.hover"
      }
    }
  ]
}
```

注意：
- `asset` 里写的是 **manifest 的名字**，不是文件路径
- 比如 `images.main_background`，必须先在 `manifest.json` 里存在

---

## 第 6 步：文件格式和命名（直接照做）

### 图片
- 推荐：PNG
- 文件名示例：
  - `main_bg.png`
  - `btn_start_normal.png`
  - `btn_start_hover.png`

### 字体
- 推荐：TTF/OTF
- 示例：`main.ttf`

### 音效
- 推荐：WAV
- 示例：`ui_click.wav`

### 命名规则（必须）
- 只用：英文小写、数字、下划线
- 不要空格，不要中文

---

## 第 7 步：交付前 30 秒自检

你只检查这 6 条：

1. 素材都放对文件夹了
2. `manifest.json` 里每个路径都写对了
3. `theme.json` 没有中文引号
4. `layout` 里的 `asset` 名字都能在 `manifest.json` 找到
5. JSON 最后一项没有多余逗号
6. 文件名没有中文和空格

---

## 第 8 步：最小可用交付（赶时间就交这个）

最少交 4 个文件：

1. `assets/images/backgrounds/main_bg.png`
2. `assets/images/buttons/btn_start_normal.png`
3. `assets/images/buttons/btn_start_hover.png`
4. `assets/manifest.json`（把上面 3 张图注册进去）

这样开发就能先接起来跑。

---

## 第 9 步：你不需要做的事

- 不需要改 Python 代码
- 不需要改核心逻辑
- 不需要理解程序架构

<<<<<<< codex/implement-headless-app-core-3pjlpu
你只要把素材 + JSON 按本说明给齐，就完成了。
=======
你只要把素材 + JSON 按本说明给齐，就完成了。（剩下的活自然有pry做）
>>>>>>> main
