# TraceLock 视觉资源契约说明

1. 这个目录是 TraceLock 的视觉资源契约。
2. 当前没有真实素材，`url` 均为 `null`。
3. 美工后续只替换 `visual_manifest.json` 中的 `url` 和 `theme.json` 中的 `style`。
4. 小游戏代码只使用 `asset_key / style_key / effect_key`。
5. 不要把真实素材路径写入 TraceLockClient。
6. 不要让 QML 直接读取 `visual_manifest.json`。
7. 资源由 Python `ResourceManager` 读取，经 `GuiBridge` 传给 QML。
8. 替换素材后应运行资源测试。
9. 不要在 manifest 中写平台上报、会话存储、数据库、输入事件、评估指标等业务字段。
10. 视觉风格应保持原创近未来赛博朋克，不使用现成商业游戏具体资产或标识。
