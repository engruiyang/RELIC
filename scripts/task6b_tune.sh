#!/usr/bin/env bash
set -euo pipefail
TRIALS="${TASK6B_TRIALS:-100}"
mkdir -p reports config
python -m ui_cli.tune_task6b \
  --input "logs/task6b/*.jsonl" \
  --labels "labels/task6b/*.yaml" \
  --base-config config/task6b.yaml \
  --trials "$TRIALS" \
  --method random \
  --out config/task6b_tuned_candidates.json
cp config/task6b_tuned_candidates.json reports/task6b_tune_report.json
