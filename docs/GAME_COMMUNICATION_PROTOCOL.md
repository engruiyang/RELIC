# GAME_COMMUNICATION_PROTOCOL

## Scope
This document defines the frozen Task7/Task8A runtime communication contract between host runtime and game side.

- Contract source of truth: `runtime/runtime_messages.py`
- This doc must not redefine semantics inconsistently.

## 1) RuntimeSnapshotView

Fields:
- `schema_version`
- `session_id`
- `now_ms`
- `user_id`
- `game_id`
- `attention`, `attention_age_ms`, `attention_fresh`
- `gyro_x`, `gyro_y`, `gyro_z`, `gyro_age_ms`, `gyro_fresh`
- `sqi`, `quality_state`
- `fi_raw`, `fi_smoothed`, `fi_valid`, `fi_confidence`
- `control_state`, `control_state_reason`
- `warning_flags`, `error_flags`

Notes:
- Must be JSON serializable.
- Produced by runtime/core side; game must consume as read-only input.

## 2) RuntimeCommand

Fields:
- `schema_version`
- `command_id`
- `session_id`
- `game_id`
- `command_type`
- `issued_at_ms`
- `payload`

Supported `command_type`:
- `start_game`
- `pause_game`
- `resume_game`
- `stop_game`
- `set_difficulty`
- `set_feedback_mode`

## 3) GameEvent

Fields:
- `schema_version`
- `event_id`
- `session_id`
- `game_id`
- `event_type`
- `created_at_ms`
- `payload`

Supported `event_type`:
- `score_update`
- `behavior_sample`
- `difficulty_request`
- `game_completed`
- `game_error`
- `user_action`

## 4) Payload schemas

### `behavior_sample`
Recommended payload keys:
- `window_ms`
- `target_count`
- `correct_count`
- `omission_count`
- `false_action_count`
- `action_count`
- `rt_samples_ms`
- `accuracy`
- `omission`
- `false_action`
- `rt_stability`

### `score_update`
- `score`
- `score_delta`
- `combo`
- `level`

### `difficulty_request`
- `requested_level`
- `reason`
- `confidence`

### `game_completed`
- `reason`
- `final_score`
- `user_finished`

### `game_error`
- `code`
- `message`
- `recoverable`

### `user_action`
- `action_type`
- `target_id`
- `success`
- `rt_ms`

## 5) Permission boundary
- Games cannot directly access DeviceAdapter/DataCenter internals/SQLite/CalibrationManager/StateMachine.
- Games cannot directly create/end training sessions.
- Games may emit `difficulty_request`; approval must be done by host/coordinator.
- Games may emit `game_completed`; whether session ends is decided by host/session orchestration.

## 6) Task7 logging behavior
- SessionManager records standard `GameEvent` entries and runtime snapshots.
- SessionManager validates session/game identity before accepting GameEvent.
- High-frequency event stream goes to `logs/sessions/*.jsonl`.
- Summary goes to SQLite `training_sessions`.

## 7) Task8 compliance requirement
- Task8 FakeGame client must follow this protocol strictly.
- Future WebSocket/Pygame transports must preserve message semantics and schema constraints.
