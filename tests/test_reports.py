from app.metrics import BatchMetrics
from app.reports import build_batch_summary


def test_build_batch_summary_includes_failure_counts():
    metrics = BatchMetrics(accepted=1, unresolved=2, invalid=3, timeout=4)

    summary = build_batch_summary(metrics)

    assert summary["accepted"] == 1
    assert summary["invalid"] == 3


def test_build_batch_summary_can_include_run_metadata():
    metrics = BatchMetrics(accepted=1, unresolved=2, invalid=3, timeout=4)

    summary = build_batch_summary(
        metrics,
        run_metadata={
            "case_concurrency": 2,
            "run_mode": "interactive",
            "delivery_dir": "delivery",
        },
    )

    assert summary["case_concurrency"] == 2
    assert summary["run_mode"] == "interactive"
    assert summary["delivery_dir"] == "delivery"
