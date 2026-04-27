#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export USE_CLASH_PROXY="${USE_CLASH_PROXY:-1}"
export ENABLE_GITHUB_ARCHIVE_FALLBACK="${ENABLE_GITHUB_ARCHIVE_FALLBACK:-1}"

cd "$ROOT_DIR"
bash scripts/run_trial.sh
bash scripts/show_case_report.sh "${1:-}" "${2:-case-0001}"
