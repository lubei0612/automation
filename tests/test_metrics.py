from app.metrics import BatchMetrics


def test_batch_metrics_tracks_failure_buckets():
    metrics = BatchMetrics()
    metrics.invalid += 1
    metrics.timeout += 2

    assert metrics.invalid == 1
    assert metrics.timeout == 2
