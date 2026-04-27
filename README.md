# Automation

Python batch automation for processing Feishu agentic-coding data packages.

The project scans candidate zip files from `input_zips/`, extracts case metadata, runs agent/code workflows, materializes SWE-style artifacts, and writes accepted/unresolved/invalid/timeout batch outputs under `batches/`.

## Repository Layout

- `app/`: core pipeline code.
- `tests/`: pytest coverage for extraction, scheduling, Docker validation, artifact generation, and reports.
- `docs/`: Feishu rules and worker setup notes.
- `scripts/`: runnable helpers for one-case trials, repo-cache warming, reports, and proxy wrapping.
- `input_zips/`: candidate zip input directory.
- `batches/`: batch outputs. Runtime workspaces are ignored; the latest curated delivery artifacts are kept.
- `repo_cache/`: optional local Git repo cache. Cache contents are ignored.

## Quick Check

```bash
python3 -m pytest -q
```

## Run A Trial

Put candidate zip files in `input_zips/`, then run:

```bash
bash scripts/run_trial.sh
```

For the current ESLint case, the Docker-validated delivery artifact is:

```text
batches/2026-04-27-batch-001/delivery/case-0001
```

The delivery image was verified with:

```bash
docker build -t automation-eslint-10368:20260427-fixed batches/2026-04-27-batch-001/delivery/case-0001
docker run --rm --platform linux/amd64 automation-eslint-10368:20260427-fixed bash -lc "python /verification/run_verification.py && cat /verification/results.json"
```

Expected verification summary:

```text
resolved: true
pre_patch_exit_code: 4
post_patch_exit_code: 0
```

Note: the Dockerfile targets `linux/amd64` because this old ESLint dependency chain includes `phantomjs-prebuilt`, which does not install on native `linux/arm64`.

