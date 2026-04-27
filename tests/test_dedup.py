from app.dedup import DedupOutcome


def test_dedup_outcome_requires_completed_flag():
    outcome = DedupOutcome(completed=False, duplicate_rate=None)
    assert outcome.completed is False
    assert outcome.duplicate_rate is None
