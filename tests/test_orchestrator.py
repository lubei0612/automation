from app.orchestrator import build_batch_id


def test_build_batch_id_uses_date_prefix():
    batch_id = build_batch_id("2026-04-24", 1)
    assert batch_id == "2026-04-24-batch-001"
