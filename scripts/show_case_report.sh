#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BATCHES_DIR="$ROOT_DIR/batches"

batch_id="${1:-}"
case_id="${2:-case-0001}"

if [[ -z "$batch_id" ]]; then
  batch_id="$(find "$BATCHES_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | grep -v '^_template_batch$' | sort | tail -n 1)"
fi

if [[ -z "$batch_id" ]]; then
  echo "no batch found under $BATCHES_DIR" >&2
  exit 1
fi

report_path=""
for classification in accepted unresolved invalid timeout; do
  candidate="$BATCHES_DIR/$batch_id/$classification/$case_id/acceptance_report.json"
  if [[ -f "$candidate" ]]; then
    report_path="$candidate"
    break
  fi
done

if [[ -z "$report_path" ]]; then
  echo "acceptance_report.json not found for batch=$batch_id case=$case_id" >&2
  exit 1
fi

ls "$(dirname "$report_path")"
cat "$report_path"
