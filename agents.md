# AGENTS.md

## 项目定位

本仓库是 RELIC / 意念玩家：基于单通道脑机头环的专注力训练系统。

当前项目重点不是先做完整 GUI 或完整小游戏，而是先建立稳定的软件主程序根基：

1. 已验证的数据桥接模块负责连接官方平台、解帧、解析、记录和输出 RealtimeSnapshot。
2. App Core 负责生命周期、输入抽象、校准、SQI、FI 接口、Session、游戏插件接口和资源协议。
3. 正式 GUI 后续作为独立 UI Adapter 接入，不要让核心逻辑依赖具体 UI 框架。
4. 小游戏通过统一 BaseGame 接口接入，不允许直接访问 socket、IPC JSON 或原始日志。

## 当前最重要的架构规则

- 不要重写已经验证过的 IPC 解帧和解析逻辑。
- 不要在 UI 或小游戏中直接连接 socket。
- 不要在小游戏中直接解析 `ipc_algorithm_test`。
- 不要让小游戏直接写原始日志。
- 不要把 UI 颜色、字体、图片、控件位置硬编码进游戏逻辑。
- 不要一次性实现所有小游戏。
- 不要一次性生成十几个复杂模块并填满实现。
- 先写小而稳定的核心，再逐步扩展。

## 数据桥接模块

数据桥接模块的正式职责：

- 连接华南脑控 / 科创平台 TCP 端口。
- 接收 4 字节大端序长度头 + UTF-8 JSON payload。
- 解析 `ipc_user_info`。
- 解析 `ipc_algorithm_test`。
- 解析 attention 注意力值。
- 解析 gyroscope / focus 数据。
- 记录 raw 日志和 sensor 日志。
- 维护 `get_snapshot()`。

当前已知事实：

- gyroscope / focus 数据频率明显高于 attention。
- attention 是较低频率夹杂输出。
- 游戏循环不能假设每一帧都有新的 attention。
- 游戏应读取 RealtimeSnapshot：focus/gyro 使用最新值，attention 使用最近一次值，并检查 `attention_age_ms`。

## 当前真实可用输入

当前主程序和小游戏可以使用：

1. 鼠标输入。
2. 键盘输入。
3. 平台输出的 attention 数值。
4. 平台输出的 focus_x / focus_y。
5. 平台输出的 gyroscope_x / gyroscope_y / gyroscope_z。
6. 游戏行为事件，例如点击、命中、遗漏、误触、反应时。

不要假设当前已经能稳定获取原始 EEG 频域数据。高阶 `ipc_device_data` 以后再考虑。

## App Core 设计原则

App Core 必须 UI 无关。它可以被命令行、PyQt GUI、后续游戏窗口或官方平台嵌入界面复用。

App Core 应提供：

- 应用生命周期管理。
- 数据桥接启动/停止封装。
- RealtimeSnapshot 读取。
- 输入事件抽象。
- 坐标映射接口。
- 资源与主题协议。
- Session 和游戏事件日志。
- 快速检查和校准流程接口。
- SQI 质量判断接口。
- FI 和状态机接口。
- 动态难度接口。
- BaseGame 小游戏插件接口。
- cleanup / dispose 资源清理约定。

## UI 和美术接入原则

后期会有专门 UI / 美术设计人员，因此代码必须预留完整素材接口。

必须使用设计 token 和资源 manifest：

- 颜色通过 theme json 管理。
- 字体通过 theme json 管理。
- 图片、音效、动画路径通过 manifest 管理。
- 页面布局可以通过 layout json 描述。
- 游戏逻辑不能写死具体图片路径。
- 游戏逻辑不能写死 UI 颜色。
- 游戏逻辑不能写死最终页面布局。

正式 GUI 以后放在 `ui_pyqt/` 或其他 UI adapter 目录，不要写进 App Core。

## 推荐目录

推荐逐步形成以下结构：

```text
relic_data_bridge.py

relic_core/
  __init__.py
  runtime.py
  models.py
  input.py
  session.py
  calibration.py
  quality.py
  focus.py
  difficulty.py
  game_api.py
  assets.py
  coordinates.py

games/
  __init__.py
  empty_game.py
  fragment_lock.py

ui_cli/
  run_core_debug.py

ui_pyqt/
  main_window.py
  qt_adapter.py

assets/
  manifest.json
  themes/
    default/theme.json
  layouts/
  images/
  icons/
  fonts/
  sounds/
  animations/

config/
  default_config.json

profiles/
logs/
third_party/
  hnnk_demo/
