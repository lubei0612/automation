from app.artifacts import build_acceptance_report, build_instance_record


def test_build_instance_record_includes_required_fields():
    record = build_instance_record(
        instance_id="eslint__eslint-10368",
        repo="eslint/eslint",
        base_commit="abc123",
        language="JavaScript",
        task_category="bug_fix",
        problem_statement="Fix lint failure",
        fail_to_pass=["tests/test_a.js"],
        pass_to_pass=["tests/test_b.js"],
        patch="diff --git a/a b/a\n",
        test_patch="diff --git a/tests/a b/tests/a\n",
    )

    assert record["instance_id"] == "eslint__eslint-10368"
    assert record["task_category"] == "bug_fix"
    assert record["FAIL_TO_PASS"] == ["tests/test_a.js"]


def test_build_acceptance_report_captures_gate_results():
    report = build_acceptance_report(
        case_id="case-0001",
        accepted=False,
        classification="unresolved",
        failed_gates=["patch_verification"],
    )

    assert report["case_id"] == "case-0001"
    assert report["accepted"] is False
    assert report["failed_gates"] == ["patch_verification"]
