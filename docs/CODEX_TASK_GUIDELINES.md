# CODEX_TASK_GUIDELINES

## Engineering constraints (archived for future tasks)
1. Do not pile business logic into `main.py`.
2. Do not pile all logic into `AppController`.
3. Keep module responsibility clear and narrow.
4. Pass cross-module data through interfaces/messages, not hidden shared state.
5. Games must not access `DeviceAdapter` directly.
6. Games must not access DataCenter internal variables directly.
7. Games must not access SQLite directly.
8. Games must not create/end `TrainingSession` directly.
9. Games must not mutate StateMachine directly.
10. Games must not read `CalibrationManager` directly.
11. Platform IPC protocol logic stays under `platform/` modules.
12. Real device protocol logic stays under `device/` modules.
13. Keep JSONL high-frequency logs and SQLite summaries separated.
14. Runtime API messages must stay JSON serializable.
15. For out-of-scope features, keep interface placeholders only; do not over-implement.
16. Every task report must include: changed files, commands run, test results, known limits.

## Task8-specific preconditions
- Do not implement pygame/websocket/report-upload/replay-adapter unless task explicitly asks.
- Do not change Task6B formulas under Task8 prep.
- Do not change runtime message semantics without contract task approval.
