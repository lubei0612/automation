from typing import Dict, Optional

from app.metrics import BatchMetrics


def build_batch_summary(metrics: BatchMetrics, run_metadata: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    summary: Dict[str, object] = {
        "accepted": metrics.accepted,
        "unresolved": metrics.unresolved,
        "invalid": metrics.invalid,
        "timeout": metrics.timeout,
    }
    if run_metadata:
        summary.update(run_metadata)
    return summary
