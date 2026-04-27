# Clash Proxy Setup

This project can route Git and cache-warming traffic through a local ClashX proxy.

Defaults:

- HTTP proxy: `http://127.0.0.1:7890`
- SOCKS proxy: `socks5h://127.0.0.1:7891`

Usage:

```bash
USE_CLASH_PROXY=1 bash scripts/run_trial.sh
USE_CLASH_PROXY=1 bash scripts/warm_repo_cache.sh repo_cache eslint/eslint
```

Or wrap any command:

```bash
bash scripts/with_clash_proxy.sh git ls-remote https://github.com/eslint/eslint.git HEAD
```

The app and scripts will also auto-enable the proxy when ClashX is already listening on `7890`.
If ClashX is not running, unset `USE_CLASH_PROXY` and use a local repo cache instead.
