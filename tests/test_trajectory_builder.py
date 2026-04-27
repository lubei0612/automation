from app.trajectory_builder import build_trajectory_record


def test_build_trajectory_record_includes_metadata_and_turn_count():
    record = build_trajectory_record(
        instance_id="eslint__eslint-10368",
        instruction="Fix the issue",
        instance={"repo": "eslint/eslint"},
        metadata={"agent": "codex"},
        trajectory=[{"role": "user"}, {"role": "assistant"}],
    )

    assert record["instance_id"] == "eslint__eslint-10368"
    assert record["metadata"]["agent"] == "codex"
    assert record["metrics"]["turn_count"] == 1
