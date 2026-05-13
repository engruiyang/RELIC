# GAME_VIEW_STATE_PROTOCOL

## 1. 协议目标
- 让游戏逻辑与渲染实现解耦。
- 让 Pygame/Web/平台嵌入共用同一视图状态。
- 保证未来 renderer 可以替换。

## 2. GameViewState 字段表
- schema_version
- session_id
- game_id
- view_type
- updated_at_ms
- status
- score
- combo
- level
- control_state
- quality_state
- feedback_hint
- hud
- entities
- effects
- layout_hints

## 3. JSON 示例
```json
{
  "schema_version": "game_view.v1",
  "session_id": "session_xxx",
  "game_id": "fake_game",
  "view_type": "fake_status",
  "updated_at_ms": 123456,
  "status": "running",
  "score": 120,
  "combo": 3,
  "level": 1,
  "control_state": "STABLE_FOCUS",
  "quality_state": "ok",
  "feedback_hint": "stable",
  "hud": {"fi": 72.0, "sqi": 0.91, "attention": 65, "message": "保持稳定"},
  "entities": [{"id":"target_1","type":"target","x":0.5,"y":0.5,"size":0.1,"state":"active","label":"target"}],
  "effects": [{"type":"highlight","target_id":"target_1","intensity":0.8,"ttl_ms":500}],
  "layout_hints": {"preferred_aspect":"16:9","safe_area":[0.05,0.05,0.9,0.9],"theme":"default"}
}
```

## 4/5/6 结构约定
- entities: list[dict]
- effects: list[dict]
- layout_hints: dict（仅布局提示，不绑定渲染框架）

## 7. Renderer 禁止访问模块
- DeviceAdapter
- DataCenter
- SQLiteStore
- SessionManager
- CalibrationManager
- StateMachine

## 8. 输入回流规则
- 控制类输入 -> RuntimeCommand（pause/resume/stop/set_feedback_mode）
- 用户动作输入 -> GameEvent.user_action

## 9. 版本策略
- 当前 schema_version = game_view.v1
- 破坏性变更升级为 game_view.v2
