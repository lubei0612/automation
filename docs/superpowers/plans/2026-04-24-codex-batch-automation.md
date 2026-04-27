# Codex Batch Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a high-confidence batch automation system that ingests candidate task zip files, runs strict preflight and verification, drives agent execution through a configurable adapter, and outputs vendor-ready delivery bundles plus separated failure buckets.

**Architecture:** A Python orchestration app manages batch state, per-case workspaces, resource-aware concurrency, Docker-backed verification, and artifact generation. A pluggable agent adapter encapsulates `codex CLI` invocation and raw session capture. Acceptance gates remain stricter than throughput goals: bad or uncertain cases must not enter `accepted/`.

**Tech Stack:** Python 3.11+, pytest, zipfile/pathlib/subprocess, JSON/JSONL, Docker CLI, codex CLI adapter, Windows-compatible process and path handling.

---

### Task 1: Scaffold project structure and configuration model

**Files:**
- Create: `app/__init__.py`
- Create: `app/config.py`
- Create: `app/paths.py`
- Create: `app/models.py`
- Create: `tests/test_config.py`
- Create: `tests/test_paths.py`

- [ ] **Step 1: Write the failing config tests**

```python
from pathlib import Path

from app.config import BatchConfig, RunMode


def test_batch_config_defaults_to_interactive_mode():
    config = BatchConfig(input_dir=Path("input_zips"), output_root=Path("batches"))
    assert config.run_mode is RunMode.INTERACTIVE
    assert config.case_timeout_minutes == 60


def test_batch_config_allows_override_values():
    config = BatchConfig(
        input_dir=Path("in"),
        output_root=Path("out"),
        run_mode=RunMode.DEDICATED,
        max_case_concurrency=3,
    )
    assert config.run_mode is RunMode.DEDICATED
    assert config.max_case_concurrency == 3
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_config.py tests/test_paths.py -v`
Expected: FAIL with import errors for missing `app.config` / `app.paths`

- [ ] **Step 3: Write minimal configuration and path models**

```python
# app/config.py
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class RunMode(str, Enum):
    INTERACTIVE = "interactive"
    DEDICATED = "dedicated"


@dataclass(slots=True)
class BatchConfig:
    input_dir: Path
    output_root: Path
    run_mode: RunMode = RunMode.INTERACTIVE
    case_timeout_minutes: int = 60
    max_case_concurrency: int | None = None
    model_name: str | None = None
```

```python
# app/paths.py
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class BatchPaths:
    batch_root: Path
    accepted_dir: Path
    unresolved_dir: Path
    invalid_dir: Path
    timeout_dir: Path
    reports_dir: Path
    workspace_dir: Path
    manifests_dir: Path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_config.py tests/test_paths.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/__init__.py app/config.py app/paths.py app/models.py tests/test_config.py tests/test_paths.py
git commit -m "feat: add batch config and path scaffolding"
```

### Task 2: Implement zip discovery and extraction

**Files:**
- Create: `app/discovery.py`
- Create: `app/extraction.py`
- Create: `tests/test_discovery.py`
- Create: `tests/fixtures/zips/.gitkeep`

- [ ] **Step 1: Write the failing discovery tests**

```python
from pathlib import Path

from app.discovery import discover_zip_inputs


def test_discover_zip_inputs_only_returns_zip_files(tmp_path: Path):
    (tmp_path / "a.zip").write_bytes(b"PK")
    (tmp_path / "b.txt").write_text("ignore", encoding="utf-8")
    (tmp_path / "c.zip").write_bytes(b"PK")

    names = [p.name for p in discover_zip_inputs(tmp_path)]

    assert names == ["a.zip", "c.zip"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_discovery.py -v`
Expected: FAIL with missing `app.discovery`

- [ ] **Step 3: Write minimal discovery implementation**

```python
# app/discovery.py
from pathlib import Path


def discover_zip_inputs(input_dir: Path) -> list[Path]:
    return sorted(path for path in input_dir.iterdir() if path.is_file() and path.suffix.lower() == ".zip")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_discovery.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/discovery.py tests/test_discovery.py
git commit -m "feat: add zip discovery"
```

### Task 3: Implement case manifest and state machine

**Files:**
- Create: `app/state_machine.py`
- Create: `app/manifest.py`
- Create: `tests/test_state_machine.py`

- [ ] **Step 1: Write the failing state tests**

```python
import pytest

from app.state_machine import CaseState, transition


def test_transition_accepts_valid_progression():
    assert transition(CaseState.DISCOVERED, CaseState.EXTRACTED) is CaseState.EXTRACTED


def test_transition_rejects_invalid_jump():
    with pytest.raises(ValueError):
        transition(CaseState.DISCOVERED, CaseState.ACCEPTED)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_state_machine.py -v`
Expected: FAIL with missing `app.state_machine`

- [ ] **Step 3: Write minimal state machine implementation**

```python
# app/state_machine.py
from enum import Enum


class CaseState(str, Enum):
    DISCOVERED = "DISCOVERED"
    EXTRACTED = "EXTRACTED"
    PREFLIGHT_PASSED = "PREFLIGHT_PASSED"
    BASELINE_VERIFIED = "BASELINE_VERIFIED"
    AGENT_RUNNING = "AGENT_RUNNING"
    PATCH_VERIFIED = "PATCH_VERIFIED"
    ARTIFACTS_BUILT = "ARTIFACTS_BUILT"
    ACCEPTED = "ACCEPTED"
    INVALID = "INVALID"
    UNRESOLVED = "UNRESOLVED"
    TIMEOUT = "TIMEOUT"
    SYSTEM_ERROR = "SYSTEM_ERROR"


_ALLOWED = {
    CaseState.DISCOVERED: {CaseState.EXTRACTED, CaseState.INVALID, CaseState.TIMEOUT, CaseState.SYSTEM_ERROR},
    CaseState.EXTRACTED: {CaseState.PREFLIGHT_PASSED, CaseState.INVALID, CaseState.TIMEOUT, CaseState.SYSTEM_ERROR},
}


def transition(current: CaseState, target: CaseState) -> CaseState:
    allowed = _ALLOWED.get(current, set())
    if target not in allowed:
        raise ValueError(f"invalid transition: {current} -> {target}")
    return target
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_state_machine.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/state_machine.py app/manifest.py tests/test_state_machine.py
git commit -m "feat: add case state machine"
```

### Task 4: Implement input recognition and invalid-case preflight

**Files:**
- Create: `app/preflight.py`
- Create: `tests/test_preflight.py`

- [ ] **Step 1: Write the failing preflight tests**

```python
from pathlib import Path

from app.preflight import classify_case_inputs


def test_preflight_marks_missing_test_patch_invalid(tmp_path: Path):
    (tmp_path / "Dockerfile").write_text("FROM ubuntu:22.04\n", encoding="utf-8")
    result = classify_case_inputs(tmp_path)
    assert result.valid is False
    assert "test.patch" in result.errors[0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_preflight.py -v`
Expected: FAIL with missing `app.preflight`

- [ ] **Step 3: Write minimal preflight implementation**

```python
# app/preflight.py
from dataclasses import dataclass
from pathlib import Path


REQUIRED_FILES = (
    "code.patch",
    "test.patch",
    "Dockerfile",
    "setup_repo.sh",
    "setup_env.sh",
    "run_verification.py",
)


@dataclass(slots=True)
class PreflightResult:
    valid: bool
    errors: list[str]


def classify_case_inputs(case_dir: Path) -> PreflightResult:
    errors = [f"missing required file: {name}" for name in REQUIRED_FILES if not (case_dir / name).exists()]
    return PreflightResult(valid=not errors, errors=errors)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_preflight.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/preflight.py tests/test_preflight.py
git commit -m "feat: add required-file preflight"
```

### Task 5: Add Dockerfile rule checks and test-patch targeting extraction

**Files:**
- Modify: `app/preflight.py`
- Create: `tests/test_dockerfile_rules.py`
- Create: `tests/test_patch_targets.py`

- [ ] **Step 1: Write the failing Dockerfile and patch-target tests**

```python
from pathlib import Path

from app.preflight import extract_test_targets, inspect_dockerfile


def test_inspect_dockerfile_detects_missing_testbed_workdir(tmp_path: Path):
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM ubuntu:22.04\n", encoding="utf-8")
    result = inspect_dockerfile(dockerfile)
    assert result.valid is False
    assert "WORKDIR /testbed" in result.errors[0]


def test_extract_test_targets_returns_changed_test_files(tmp_path: Path):
    patch = tmp_path / "test.patch"
    patch.write_text(
        "diff --git a/tests/test_a.py b/tests/test_a.py\n"
        "--- a/tests/test_a.py\n"
        "+++ b/tests/test_a.py\n",
        encoding="utf-8",
    )
    assert extract_test_targets(patch) == ["tests/test_a.py"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_dockerfile_rules.py tests/test_patch_targets.py -v`
Expected: FAIL with missing functions

- [ ] **Step 3: Write minimal Dockerfile inspection and patch target extraction**

```python
def inspect_dockerfile(dockerfile: Path) -> PreflightResult:
    text = dockerfile.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []
    if "WORKDIR /testbed" not in text:
        errors.append("Dockerfile must set WORKDIR /testbed")
    return PreflightResult(valid=not errors, errors=errors)


def extract_test_targets(test_patch: Path) -> list[str]:
    targets: list[str] = []
    for line in test_patch.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("+++ b/tests/"):
            targets.append(line.removeprefix("+++ b/"))
    return targets
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_dockerfile_rules.py tests/test_patch_targets.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/preflight.py tests/test_dockerfile_rules.py tests/test_patch_targets.py
git commit -m "feat: inspect Dockerfile rules and patch targets"
```

### Task 6: Implement duplicate-check interface and batch-level metrics model

**Files:**
- Create: `app/dedup.py`
- Create: `app/metrics.py`
- Create: `tests/test_dedup.py`
- Create: `tests/test_metrics.py`

- [ ] **Step 1: Write the failing duplicate and metrics tests**

```python
from app.dedup import DedupOutcome
from app.metrics import BatchMetrics


def test_dedup_outcome_requires_completed_flag():
    outcome = DedupOutcome(completed=False, duplicate_rate=None)
    assert outcome.completed is False
    assert outcome.duplicate_rate is None


def test_batch_metrics_tracks_failure_buckets():
    metrics = BatchMetrics()
    metrics.invalid += 1
    metrics.timeout += 2
    assert metrics.invalid == 1
    assert metrics.timeout == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_dedup.py tests/test_metrics.py -v`
Expected: FAIL with missing modules

- [ ] **Step 3: Write minimal dedup and metrics models**

```python
# app/dedup.py
from dataclasses import dataclass


@dataclass(slots=True)
class DedupOutcome:
    completed: bool
    duplicate_rate: float | None
    notes: list[str] | None = None
```

```python
# app/metrics.py
from dataclasses import dataclass


@dataclass(slots=True)
class BatchMetrics:
    accepted: int = 0
    unresolved: int = 0
    invalid: int = 0
    timeout: int = 0
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_dedup.py tests/test_metrics.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/dedup.py app/metrics.py tests/test_dedup.py tests/test_metrics.py
git commit -m "feat: add duplicate-check interface and batch metrics"
```

### Task 7: Build codex adapter contract and session capture format

**Files:**
- Create: `app/agent_adapter.py`
- Create: `tests/test_agent_adapter.py`

- [ ] **Step 1: Write the failing agent adapter tests**

```python
from pathlib import Path

from app.agent_adapter import AgentRunRequest


def test_agent_run_request_tracks_prompt_and_workspace(tmp_path: Path):
    request = AgentRunRequest(prompt="fix bug", workspace=tmp_path, model_name=None)
    assert request.prompt == "fix bug"
    assert request.workspace == tmp_path
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_agent_adapter.py -v`
Expected: FAIL with missing `app.agent_adapter`

- [ ] **Step 3: Write minimal agent adapter request and result models**

```python
# app/agent_adapter.py
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AgentRunRequest:
    prompt: str
    workspace: Path
    model_name: str | None


@dataclass(slots=True)
class AgentRunResult:
    exit_code: int
    stdout_path: Path
    stderr_path: Path
    session_path: Path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_agent_adapter.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/agent_adapter.py tests/test_agent_adapter.py
git commit -m "feat: define agent adapter contract"
```

### Task 8: Implement trajectory conversion and turn-count validation

**Files:**
- Create: `app/trajectory.py`
- Create: `tests/test_trajectory.py`

- [ ] **Step 1: Write the failing trajectory tests**

```python
from app.trajectory import count_turns


def test_count_turns_counts_user_assistant_pairs():
    messages = [{"role": "user"}, {"role": "assistant"}, {"role": "user"}, {"role": "assistant"}]
    assert count_turns(messages) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_trajectory.py -v`
Expected: FAIL with missing `app.trajectory`

- [ ] **Step 3: Write minimal trajectory utilities**

```python
# app/trajectory.py
def count_turns(messages: list[dict]) -> int:
    return sum(1 for message in messages if message.get("role") == "assistant")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_trajectory.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/trajectory.py tests/test_trajectory.py
git commit -m "feat: add trajectory turn counting"
```

### Task 9: Implement resource-aware concurrency recommendation

**Files:**
- Create: `app/resources.py`
- Create: `tests/test_resources.py`

- [ ] **Step 1: Write the failing resource tests**

```python
from app.config import RunMode
from app.resources import MachineProfile, recommend_case_concurrency


def test_recommend_case_concurrency_is_conservative_for_interactive_mode():
    profile = MachineProfile(cpu_count=8, total_memory_gb=32, free_memory_gb=20)
    assert recommend_case_concurrency(profile, RunMode.INTERACTIVE) <= 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_resources.py -v`
Expected: FAIL with missing `app.resources`

- [ ] **Step 3: Write minimal resource recommendation implementation**

```python
# app/resources.py
from dataclasses import dataclass

from app.config import RunMode


@dataclass(slots=True)
class MachineProfile:
    cpu_count: int
    total_memory_gb: int
    free_memory_gb: int


def recommend_case_concurrency(profile: MachineProfile, run_mode: RunMode) -> int:
    if run_mode is RunMode.INTERACTIVE:
        return 1 if profile.free_memory_gb < 16 else 2
    return max(1, min(profile.cpu_count // 2, profile.free_memory_gb // 8))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_resources.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/resources.py tests/test_resources.py
git commit -m "feat: recommend conservative case concurrency"
```

### Task 10: Implement case classification and delivery folder routing

**Files:**
- Create: `app/classification.py`
- Create: `tests/test_classification.py`

- [ ] **Step 1: Write the failing classification tests**

```python
from app.classification import classify_terminal_state
from app.state_machine import CaseState


def test_classify_terminal_state_maps_invalid():
    assert classify_terminal_state(CaseState.INVALID) == "invalid"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_classification.py -v`
Expected: FAIL with missing `app.classification`

- [ ] **Step 3: Write minimal classification implementation**

```python
# app/classification.py
from app.state_machine import CaseState


def classify_terminal_state(state: CaseState) -> str:
    return {
        CaseState.ACCEPTED: "accepted",
        CaseState.UNRESOLVED: "unresolved",
        CaseState.INVALID: "invalid",
        CaseState.TIMEOUT: "timeout",
    }[state]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_classification.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/classification.py tests/test_classification.py
git commit -m "feat: add delivery bucket classification"
```

### Task 11: Build batch reports and acceptance report generation

**Files:**
- Create: `app/reports.py`
- Create: `tests/test_reports.py`

- [ ] **Step 1: Write the failing report tests**

```python
from app.metrics import BatchMetrics
from app.reports import build_batch_summary


def test_build_batch_summary_includes_failure_counts():
    metrics = BatchMetrics(accepted=1, unresolved=2, invalid=3, timeout=4)
    summary = build_batch_summary(metrics)
    assert summary["accepted"] == 1
    assert summary["invalid"] == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_reports.py -v`
Expected: FAIL with missing `app.reports`

- [ ] **Step 3: Write minimal report builder**

```python
# app/reports.py
from app.metrics import BatchMetrics


def build_batch_summary(metrics: BatchMetrics) -> dict:
    return {
        "accepted": metrics.accepted,
        "unresolved": metrics.unresolved,
        "invalid": metrics.invalid,
        "timeout": metrics.timeout,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_reports.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/reports.py tests/test_reports.py
git commit -m "feat: add batch summary reporting"
```

### Task 12: Implement top-level batch orchestrator

**Files:**
- Create: `app/orchestrator.py`
- Create: `tests/test_orchestrator.py`

- [ ] **Step 1: Write the failing orchestrator tests**

```python
from pathlib import Path

from app.config import BatchConfig
from app.orchestrator import build_batch_id


def test_build_batch_id_uses_date_prefix():
    batch_id = build_batch_id("2026-04-24", 1)
    assert batch_id == "2026-04-24-batch-001"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_orchestrator.py -v`
Expected: FAIL with missing `app.orchestrator`

- [ ] **Step 3: Write minimal orchestrator helper**

```python
# app/orchestrator.py
def build_batch_id(date_str: str, sequence: int) -> str:
    return f"{date_str}-batch-{sequence:03d}"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_orchestrator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/orchestrator.py tests/test_orchestrator.py
git commit -m "feat: add batch orchestrator scaffold"
```

### Task 13: Add machine setup guide for Windows workers

**Files:**
- Create: `docs/worker-setup.md`
- Test: manual review

- [ ] **Step 1: Write the setup guide**

Include:

```text
- required software: Python, Docker Desktop, codex CLI
- folder layout for input_zips and batches
- interactive vs dedicated mode
- how recommended concurrency is chosen
- how to start a batch run
- where accepted/unresolved/invalid/timeout outputs go
- where to inspect logs and reports
```

- [ ] **Step 2: Review the guide for missing operator steps**

Review: `docs/worker-setup.md`
Expected: no placeholders, no missing startup prerequisites

- [ ] **Step 3: Commit**

```bash
git add docs/worker-setup.md
git commit -m "docs: add worker setup guide"
```

### Task 14: End-to-end acceptance and regression coverage

**Files:**
- Create: `tests/test_end_to_end_smoke.py`
- Modify: any files needed to support test harness

- [ ] **Step 1: Write failing end-to-end smoke test**

```python
def test_smoke_batch_run_creates_delivery_buckets():
    assert False, "replace with smoke test harness for minimal synthetic zip case"
```

- [ ] **Step 2: Run smoke test to verify it fails**

Run: `pytest tests/test_end_to_end_smoke.py -v`
Expected: FAIL with explicit smoke harness placeholder failure

- [ ] **Step 3: Replace placeholder with minimal synthetic fixture and harness**

```python
def test_smoke_batch_run_creates_delivery_buckets(tmp_path):
    # create synthetic zip fixture, run orchestrator, assert output dirs exist
    ...
```

- [ ] **Step 4: Run targeted and full test suite**

Run: `pytest tests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_end_to_end_smoke.py
git commit -m "test: add end-to-end smoke coverage"
```

## Self-Review

- Spec coverage added for duplicate checking, distribution reporting, Docker rules, test-file protection, and model configurability; tasks above cover these areas.
- No placeholder implementation steps are acceptable during execution; Task 14 intentionally starts with a failing placeholder and must be replaced before the task is complete.
- Type and naming consistency to preserve during implementation:
  - `BatchConfig`, `RunMode`
  - `CaseState`
  - `PreflightResult`
  - `DedupOutcome`
  - `BatchMetrics`
  - `AgentRunRequest`, `AgentRunResult`

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-24-codex-batch-automation.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
