# Environment Checklist

## Purpose

在一台新电脑上第一次使用这套批处理系统前，先检查下面这些依赖和目录。

## Required Software

必须安装：

- `Python 3`
- `git`
- `Docker`
- `codex CLI`

## Quick Checks

建议在终端里逐条检查：

```bash
python3 --version
git --version
docker --version
codex --version
```

如果其中任何一条失败，这台机器还不能正式跑批次。

## Required Project Directories

工程根目录下至少应看到：

```text
app/
tests/
docs/
input_zips/
batches/
repo_cache/
```

其中：

- `input_zips/` 用来放候选 zip
- `batches/` 用来放批次输出
- `repo_cache/` 用来放本地仓库缓存

## Runtime Expectations

正式运行前，还应确认：

- Docker 能正常启动
- `codex CLI` 已完成登录或必要配置
- 当前机器允许执行 `git diff` 和 `git apply`
- 候选 zip 已放入 `input_zips/`

默认建议先预热仓库缓存，然后再启动批处理：

```bash
bash scripts/warm_repo_cache.sh repo_cache eslint/eslint
export REPO_CACHE_ROOT=repo_cache
```

脚本会优先以 `--mirror` 方式缓存仓库，适合反复跑同一批数据。

## Recommended Read Order

第一次使用建议先看：

1. `docs/worker-setup.md`
2. `docs/environment-checklist.md`
3. `docs/superpowers/specs/2026-04-24-codex-batch-automation-design.md`

## Start Command

当前推荐启动命令：

```bash
python3 -m app.main
```
