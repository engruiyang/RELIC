# ShardLock Visual Contract

这个目录是 **ShardLock Protocol（碎片锁定协议）** 的视觉资源契约目录。

## 当前状态
- 当前没有真实素材，`url` 字段均为 `null`。
- visual manifest 仅定义资源 key 与回退形态，不承载真实素材路径。

## 美工与队友协作规则
1. 美工后续只替换 `visual_manifest.json` 中的 `url`，以及 theme 中的 `style`。
2. 小游戏代码只使用 `asset_key` / `style_key` / `effect_key`。
3. 不要把真实素材路径写入 ShardLockClient。
4. 不要让 QML 直接读取本 manifest。
5. 资源由 Python ResourceManager 读取，经 GuiBridge 传给 QML。
6. 替换素材后应运行资源测试与契约测试。
