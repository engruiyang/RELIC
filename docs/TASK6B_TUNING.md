# TASK6B_TUNING

Task6B tuning workflow is active and should remain config-driven.

## Current status
- Estimator implementations are closed.
- Parameter tuning is pending final live-data human review.

## Workflow
1. Record data into `logs/task6b/`.
2. Maintain frame labels in `labels/task6b/*.frames.csv`.
3. Evaluate with `ui_cli.evaluate_task6b`.
4. Tune with `ui_cli.tune_task6b`.
5. Promote chosen config snapshot after review.

## Boundary
- Do not alter core formulas casually.
- Prefer `config/task6b.yaml` or tuned candidates for iteration.
- Keep tuning logs separated from session logs (`logs/sessions/`).
