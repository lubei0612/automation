#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export REPO_CACHE_ROOT="${REPO_CACHE_ROOT:-$ROOT_DIR/repo_cache}"

if [[ "${USE_CLASH_PROXY:-0}" != "0" ]]; then
  export HTTP_PROXY="${HTTP_PROXY:-http://127.0.0.1:7890}"
  export HTTPS_PROXY="${HTTPS_PROXY:-http://127.0.0.1:7890}"
  export ALL_PROXY="${ALL_PROXY:-socks5h://127.0.0.1:7891}"
  export NO_PROXY="${NO_PROXY:-localhost,127.0.0.1,::1}"
  export http_proxy="${http_proxy:-$HTTP_PROXY}"
  export https_proxy="${https_proxy:-$HTTPS_PROXY}"
  export all_proxy="${all_proxy:-$ALL_PROXY}"
  export no_proxy="${no_proxy:-$NO_PROXY}"
fi

cd "$ROOT_DIR"
python3 -m app.main
