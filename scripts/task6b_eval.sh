#!/usr/bin/env bash
set -euo pipefail
mkdir -p reports
python -m ui_cli.evaluate_task6b \
  --input "logs/task6b/*.jsonl" \
  --labels "labels/task6b/*.yaml" \
  --config config/task6b.yaml \
  --out reports/task6b_eval.json
