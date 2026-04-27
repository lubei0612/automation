#!/bin/bash
set -euo pipefail

export HTTP_PROXY="${HTTP_PROXY:-http://127.0.0.1:7890}"
export HTTPS_PROXY="${HTTPS_PROXY:-http://127.0.0.1:7890}"
export ALL_PROXY="${ALL_PROXY:-socks5h://127.0.0.1:7891}"
export NO_PROXY="${NO_PROXY:-localhost,127.0.0.1,::1}"

exec "$@"
