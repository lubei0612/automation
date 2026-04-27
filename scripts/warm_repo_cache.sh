#!/bin/bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "usage: $0 <repo_cache_root> <owner/repo> [<owner/repo> ...]" >&2
  exit 1
fi

repo_cache_root="$1"
shift

git_proxy_args=()
if [[ "${USE_CLASH_PROXY:-0}" != "0" ]]; then
  export HTTP_PROXY="${HTTP_PROXY:-http://127.0.0.1:7890}"
  export HTTPS_PROXY="${HTTPS_PROXY:-http://127.0.0.1:7890}"
  export ALL_PROXY="${ALL_PROXY:-socks5h://127.0.0.1:7891}"
  export NO_PROXY="${NO_PROXY:-localhost,127.0.0.1,::1}"
  export http_proxy="${http_proxy:-$HTTP_PROXY}"
  export https_proxy="${https_proxy:-$HTTPS_PROXY}"
  export all_proxy="${all_proxy:-$ALL_PROXY}"
  export no_proxy="${no_proxy:-$NO_PROXY}"
  git_proxy_args=(-c "http.proxy=${HTTP_PROXY}" -c "https.proxy=${HTTPS_PROXY}")
fi

mkdir -p "$repo_cache_root"

for repo_spec in "$@"; do
  owner="${repo_spec%%/*}"
  repo="${repo_spec##*/}"
  target="$repo_cache_root/${owner}__${repo}"

  if [ -d "$target" ] && git -C "$target" rev-parse --is-bare-repository >/dev/null 2>&1; then
    echo "[skip] $repo_spec already cached as bare repo at $target"
    continue
  fi

  if [ -d "$target/.git" ]; then
    echo "[skip] $repo_spec already cached as working tree at $target"
    continue
  fi

  echo "[clone] $repo_spec -> $target"
  if [ "${#git_proxy_args[@]}" -gt 0 ]; then
    git "${git_proxy_args[@]}" clone --mirror "https://github.com/${owner}/${repo}.git" "$target"
  else
    git clone --mirror "https://github.com/${owner}/${repo}.git" "$target"
  fi
done
