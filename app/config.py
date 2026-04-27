from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class RunMode(str, Enum):
    INTERACTIVE = "interactive"
    DEDICATED = "dedicated"


@dataclass(frozen=True)
class BatchConfig:
    input_dir: Path
    output_root: Path
    repo_cache_root: Optional[Path] = None
    run_mode: RunMode = RunMode.INTERACTIVE
    case_timeout_minutes: int = 60
    max_case_concurrency: Optional[int] = None
    model_name: Optional[str] = None
