from dataclasses import dataclass


@dataclass
class BatchMetrics:
    accepted: int = 0
    unresolved: int = 0
    invalid: int = 0
    timeout: int = 0
