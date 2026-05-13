# ARCHITECTURE_OVERVIEW

## End-to-end flow

PlatformGateway / DeviceAdapter  
↓  
DataCenter / RealtimeSnapshot  
↓  
QualityGate / FocusEstimator / ControlStateEstimator  
↓  
RuntimeSnapshotView  
↓  
Runtime API  
↓  
GameManager / GameClient  
↓  
GameEvent  
↓  
SessionManager  
↓  
JSONL + SQLite Summary

## Key boundaries
1. **DataCenter is the real-time source of truth** for attention/gyro freshness and stream state.
2. **Task6B estimators** are responsible for SQI/FI/control_state outputs.
3. **Runtime API is the only host↔game boundary**; game logic must not bypass it.
4. **SessionManager records only**; it does not re-derive FI/SQI/control state formulas.
5. **Storage split is intentional**:
   - JSONL: high-frequency event stream (`session_start`, `runtime_snapshot`, `game_event`, ...)
   - SQLite: low-frequency session summary (`training_sessions`)
6. **`logs/task6b/` is for tuning/evaluation datasets**, not formal training session logs.
7. **`logs/sessions/` is for Task7+ formal training session logs**.

## Task8 guardrail
Before implementing GameManager/FakeGame client behavior, preserve:
- Runtime contract semantics (`runtime/runtime_messages.py`).
- Session logging semantics (`session/session_manager.py`).
- Storage contract for `training_sessions` summary row fields.
