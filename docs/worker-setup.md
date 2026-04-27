# Worker Setup

## Purpose

这台机器用于批量处理候选题目 zip 包，并产出可交付与不可交付的分类结果目录。

## Required Software

- Python 3.9+
- Docker Desktop
- `codex CLI`

## Expected Directory Layout

```text
automation/
  input_zips/
  batches/
  app/
  tests/
  docs/
```

将候选 zip 包放入 `input_zips/`。

## Run Modes

- `interactive`
  机器会边跑任务边正常使用，系统应保守分配并发。
- `dedicated`
  机器专门用于跑批处理，可以提高并发。

默认推荐先使用 `interactive`。

## Concurrency

系统应根据机器资源自动估算建议并发，并将最终采用的并发写入批次报告。

如果这台机器仍要日常使用，优先保持低并发。

## Batch Outputs

每次批处理会产出：

- `delivery/`
- `accepted/`
- `unresolved/`
- `invalid/`
- `timeout/`
- `reports/`

`delivery/` 是对外交付的最终目录视图，只同步 `accepted/` 的内容。
`accepted/` 保留内部运行产物，便于排查。

## Startup

当前建议优先使用一键入口：

```bash
bash scripts/run_case_once.sh
```

它会自动：

- 开启 Clash 代理环境
- 开启 GitHub archive fallback
- 运行批处理
- 打印最新 case 的 `acceptance_report.json`

底层 Python 主入口仍然可用：

```bash
python3 -m app.main
```

如果后续增加专门的脚本入口，以脚本入口为准。

## Repo Cache

默认推荐先预热本地仓库缓存再启动：

```bash
bash scripts/warm_repo_cache.sh repo_cache eslint/eslint
export REPO_CACHE_ROOT=repo_cache
```

之后再启动批处理。

预热脚本默认以 `--mirror` 方式缓存仓库，适合反复试跑和多机复用。

## One-Shot Trial

在已预热好 repo cache 或已配置代理的机器上，可以直接运行：

```bash
bash scripts/run_trial.sh
```

查看最新 case 结果：

```bash
bash scripts/show_case_report.sh
```

## Runtime Overrides

可通过环境变量控制运行模式：

```bash
export AUTOMATION_RUN_MODE=interactive
export AUTOMATION_MAX_CASE_CONCURRENCY=2
export AUTOMATION_MODEL_NAME=gpt-5.5
```

- `AUTOMATION_RUN_MODE`
  可选 `interactive` / `dedicated`
- `AUTOMATION_MAX_CASE_CONCURRENCY`
  显式覆盖自动并发
- `AUTOMATION_MODEL_NAME`
  指定 Codex CLI 使用的模型

## Logs and Troubleshooting

优先查看：

- `reports/batch_summary.md`
- `reports/batch_summary.json`
- `reports/failures.csv`
- 各 case 的 workspace 和 manifest 文件

## Operator Notes

- 不要把坏样本混进 `accepted/`
- 如果甲方后续锁定模型，需要在配置层切换到指定模型
- 如果机器明显变卡，应降低并发或使用 `interactive` 模式
