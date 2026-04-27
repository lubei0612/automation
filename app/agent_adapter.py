from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class AgentRunRequest:
    prompt: str
    workspace: Path
    model_name: Optional[str]


@dataclass(frozen=True)
class AgentRunResult:
    exit_code: int
    stdout_path: Path
    stderr_path: Path
    session_path: Path
