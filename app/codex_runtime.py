from pathlib import Path
from typing import Callable, Optional

from app.codex_runner import build_codex_command
from app.executor import CommandExecutionResult, run_command


def run_codex_task(
    *,
    prompt: str,
    workspace: Path,
    model_name: Optional[str],
    executor: Callable[..., CommandExecutionResult] = run_command,
    timeout_seconds: float = 1800.0,
) -> CommandExecutionResult:
    command = build_codex_command(
        prompt=prompt,
        workdir=str(workspace),
        model_name=model_name,
    )
    return executor(command, cwd=workspace, timeout_seconds=timeout_seconds)
