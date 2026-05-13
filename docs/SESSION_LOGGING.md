# SESSION_LOGGING

## 1) Purpose
Task7 session logging stores:
- high-frequency events in JSONL
- low-frequency session summary in SQLite

SessionManager records provided runtime/game messages and **does not recompute Task6B formulas**.

## 2) Directory split
- `logs/sessions/`: formal training session logs
- `logs/task6b/`: Task6B data collection/tuning artifacts only

Do not write session JSONL to `logs/task6b/`.

## 3) JSONL line format
Each line is a JSON object:
- `ts`
- `event_type`
- `session_id`
- `payload`

## 4) Typical event sequence
1. `session_start`
2. repeated `runtime_snapshot`
3. optional repeated `game_event`
4. `session_summary`
5. `session_end`

## 5) Example events
- `session_start`: includes `user_id`, `game_id`, `calibration_id`, `log_path`
- `runtime_snapshot`: RuntimeSnapshotView payload for that tick
- `game_event`: serialized GameEvent payload
- `session_summary`: full Task7A+Task7B summary row
- `session_end`: session status/end reason

## 6) SQLite summary table (`training_sessions`)
Includes Task7A fields plus Task7B fields, including:
- Durations/ticks: `total_duration_ms`, `observed_tick_count`, `valid_tick_count`, `warning_tick_count`, `unreliable_tick_count`, `valid_duration_ms`, `warning_duration_ms`, `unreliable_duration_ms`
- State summaries: `quality_state_summary`, `quality_state_duration_summary`, `control_state_summary`, `control_state_duration_summary`
- FI/SQI summary: `final_fi_avg`, `final_sqi_avg`, `fi_min`, `fi_max`, `fi_last`, `sqi_min`, `sqi_max`, `sqi_last`
- GameEvent summary: `game_event_count`, `score_update_count`, `behavior_sample_count`, `user_action_count`, `game_error_count`, `score_last`, `score_max`, `score_total_delta`, `game_completed`, `game_completion_reason`

## 7) Duration semantics
- `valid_duration_ms`: tick duration sum where quality is `ok` and `fi_valid=True`.
- `warning_duration_ms`: tick duration sum where quality is `warning`.
- `unreliable_duration_ms`: tick duration sum where control state is `UNRELIABLE_SIGNAL` or quality is `invalid/error`.

`warning_duration_ms` and `unreliable_duration_ms` can overlap because they represent different semantic dimensions.

## 8) GameEvent aggregation semantics
- `score_update` updates score counters/fields.
- `behavior_sample` increments behavior sample count and marks `has_behavior_samples`.
- `user_action` increments action count.
- `game_error` increments game error count and session error count.
- `game_completed` marks completion state and reason, optional final score.
- `difficulty_request` is logged only; not approved by SessionManager.

## 9) CLI usage
```bash
python -m ui_cli.run_session_debug --mode demo --duration-sec 10 --user-id demo_user --db-path data/relic_local.db
python -m ui_cli.run_session_debug --list-sessions --db-path data/relic_local.db
python -m ui_cli.run_session_debug --show-session SESSION_ID --db-path data/relic_local.db
python -m ui_cli.run_session_debug --show-log-path SESSION_ID --db-path data/relic_local.db
```

## 10) Boundary reminder
SessionManager consumes already-computed RuntimeSnapshotView fields and does not recalculate FI/SQI/control formulas.
