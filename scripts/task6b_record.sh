#!/usr/bin/env bash
set -euo pipefail
BRIDGE="${1:-}"; USER_ID="${2:-}"; DURATION="${3:-}"; TAG="${4:-}"
if [[ -z "$BRIDGE" || -z "$USER_ID" || -z "$DURATION" || -z "$TAG" ]]; then
  echo "Usage: bash scripts/task6b_record.sh <bridge> <user_id> <duration_sec> <tag>"; exit 1
fi
TS=$(date +"%Y%m%d_%H%M%S")
SESSION_ID="task6b_${BRIDGE}_${USER_ID}_${TAG}_${TS}"
LOG_PATH="logs/task6b/${SESSION_ID}.jsonl"
LABEL_PATH="labels/task6b/${SESSION_ID}.yaml"
mkdir -p logs/task6b labels/task6b
if [[ "$BRIDGE" == "mock" ]]; then
  python -m ui_cli.run_core_debug --bridge mock --mode demo --session-id "$SESSION_ID" --duration-sec "$DURATION" --record-jsonl "$LOG_PATH" --label-template "$LABEL_PATH"
else
  python -m ui_cli.run_core_debug --bridge live --mode user --user-id "$USER_ID" --host 127.0.0.1 --port 8000 --session-id "$SESSION_ID" --duration-sec "$DURATION" --record-jsonl "$LOG_PATH" --label-template "$LABEL_PATH"
fi
echo "Recorded JSONL:"
echo "$LOG_PATH"
echo "Label file:"
echo "$LABEL_PATH"
echo "Next step:"
echo "Edit the label file, then run:"
echo "bash scripts/task6b_eval.sh"
echo "bash scripts/task6b_tune.sh"
