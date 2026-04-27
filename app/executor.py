from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
from typing import List

from app.proxy import apply_clash_proxy_env

@dataclass(frozen=True)
class CommandExecutionResult:
    command: List[str]
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool


def run_command(command: List[str], *, cwd: Path, timeout_seconds: float) -> CommandExecutionResult:
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            env=apply_clash_proxy_env(os.environ),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        return CommandExecutionResult(
            command=command,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            timed_out=False,
        )
    except subprocess.TimeoutExpired as exc:
        return CommandExecutionResult(
            command=command,
            exit_code=124,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
            timed_out=True,
        )
