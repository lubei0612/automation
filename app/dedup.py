from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class DedupOutcome:
    completed: bool
    duplicate_rate: Optional[float]
    notes: Optional[List[str]] = None
