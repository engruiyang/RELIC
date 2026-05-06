# HNNK 官方示例代码

本目录保存华南脑控 / 科创平台官方 Python demo 中的参考代码。

这些文件仅用于协议理解和开发参考，不作为 RELIC 项目的正式运行代码。

请不要在本目录中编写 RELIC 的正式业务代码。

重点参考文件：

- tcp_socket_client.py：官方 TCP Socket 客户端示例，用于确认通信帧格式。
- local_socket_client.py：官方 LocalSocket 客户端示例，后续平台自动启动或管道通信模式可能参考。
- main_window.py：官方 PyQt demo 主窗口示例，展示连接端口、接收消息、解析 ipc_user_info 和 ipc_algorithm_test 的基本流程。

RELIC 自己的正式代码应放在仓库根目录、relic_core/ 或 app/ 目录中。
