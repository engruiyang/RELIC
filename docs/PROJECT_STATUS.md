# PROJECT_STATUS

## Snapshot (Pre-Task8 Cleanup)
- Date: 2026-05-13
- Scope: documentation consolidation and boundary hardening before Task8.

## Task1~Task5
- Core pipeline, user/profile/calibration flows, and baseline CLI/debug workflows are available and covered by existing tests.

## Task6B
- Completed:
  - `QualityGate`, `FocusEstimator`, `ControlStateEstimator` implementation.
  - `runtime_snapshot` output fields consumed by runtime/session flows.
  - Frame-level labeling CSV workflow.
  - Offline evaluation CLI (`evaluate_task6b`).
  - Tuning CLI (`tune_task6b`).
- Not completed:
  - Final parameter selection after live-data human review.
- Status: **implementation closed, parameter tuning pending**.
- Boundary:
  - Task6B should be tuned through config and evaluation workflow.
  - Avoid formula-level changes unless a dedicated task explicitly requests it.

## Runtime Contract
- Completed:
  - `RuntimeSnapshotView`, `RuntimeCommand`, `GameEvent`, `LocalRuntime`, `GameManifest`.
- Status: **contract frozen for Task8A**.
- Boundary:
  - Messages must remain JSON serializable.
  - Games must communicate with host only via Runtime API.

## Task7A
- Completed:
  - Minimal SessionManager loop.
  - JSONL session logs in `logs/sessions/`.
  - SQLite `training_sessions` summary persistence.

## Task7B
- Completed:
  - Duration summaries and tick counters.
  - FI/SQI min/max/last summary fields.
  - GameEvent aggregate counters.
  - Session query CLI (`--list-sessions`, `--show-session`, `--show-log-path`).
- Status: **functionally closed, docs pending**.

## Task8
- Not started.
- Entry condition:
  - Pre-Task8 cleanup done.
  - Required tests and CLI checks pass.
