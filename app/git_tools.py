from pathlib import Path
from typing import Callable

from app.executor import CommandExecutionResult, run_command


def capture_final_diff(
    workspace: Path,
    *,
    executor: Callable[..., CommandExecutionResult] = run_command,
    timeout_seconds: float = 30.0,
) -> str:
    result = executor(["git", "diff"], cwd=workspace, timeout_seconds=timeout_seconds)
    return result.stdout if result.exit_code == 0 and not result.timed_out else ""
