from dataclasses import dataclass
import os
from pathlib import Path
from typing import Callable, List, Optional

from app.baseline import build_baseline_verification_plan
from app.executor import CommandExecutionResult, run_command
from app.local_runtime import prepare_local_runtime_scripts
from app.repo_setup import extract_repo_path_from_setup_repo


@dataclass(frozen=True)
class BaselineVerificationResult:
    valid: bool
    failed_step: Optional[str]
    executions: List[CommandExecutionResult]


def _build_step_command(step: dict) -> List[str]:
    name = step["step"]
    if name in {"run_initial_tests", "run_fail_to_pass_tests", "run_regression_tests"}:
        return ["python3", "-m", "pytest", *step["targets"]]
    if name in {"apply_test_patch", "apply_code_patch"}:
        return ["git", "apply", "-v", step["patch"]]
    raise ValueError(f"unsupported baseline step: {name}")


def build_script_based_verification_commands(
    *,
    case_dir: Path,
    repo_path: str,
    repo_cache_root: Path = None,
) -> List[List[str]]:
    runtime = prepare_local_runtime_scripts(case_dir, repo_cache_root=repo_cache_root)
    return [
        ["bash", str(runtime.setup_repo_script.resolve())],
        ["bash", str(runtime.setup_env_script.resolve())],
        ["python3", str(runtime.run_verification_script.resolve())],
    ]


def verify_baseline(
    *,
    workspace: Path,
    test_targets: List[str],
    code_patch_path: str,
    test_patch_path: str,
    executor: Callable[..., CommandExecutionResult] = run_command,
    timeout_seconds: float = 300.0,
) -> BaselineVerificationResult:
    setup_repo = workspace / "setup_repo.sh"
    setup_env = workspace / "setup_env.sh"
    verification_script = workspace / "run_verification.py"

    if setup_repo.exists() and setup_env.exists() and verification_script.exists():
        repo_path = extract_repo_path_from_setup_repo(setup_repo)
        repo_cache_env = os.environ.get("REPO_CACHE_ROOT", "").strip()
        repo_cache_root = Path(repo_cache_env).expanduser().resolve() if repo_cache_env else None
        commands = build_script_based_verification_commands(
            case_dir=workspace,
            repo_path=repo_path,
            repo_cache_root=repo_cache_root,
        )
        executions: List[CommandExecutionResult] = []
        failed_step = None
        step_names = ["setup_repo", "setup_env", "run_verification"]
        for step_name, command in zip(step_names, commands):
            result = executor(command, cwd=workspace, timeout_seconds=timeout_seconds)
            executions.append(result)
            if result.exit_code != 0 or result.timed_out:
                failed_step = step_name
                break
        return BaselineVerificationResult(
            valid=failed_step is None,
            failed_step=failed_step,
            executions=executions,
        )

    plan = build_baseline_verification_plan(
        test_targets=test_targets,
        code_patch_path=code_patch_path,
        test_patch_path=test_patch_path,
    )
    executions: List[CommandExecutionResult] = []
    for step in plan:
        command = _build_step_command(step)
        result = executor(command, cwd=workspace, timeout_seconds=timeout_seconds)
        executions.append(result)
        if result.exit_code != 0 or result.timed_out:
            return BaselineVerificationResult(
                valid=False,
                failed_step=step["step"],
                executions=executions,
            )
    return BaselineVerificationResult(valid=True, failed_step=None, executions=executions)
