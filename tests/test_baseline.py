from app.baseline import build_baseline_verification_plan


def test_build_baseline_verification_plan_orders_test_and_code_patch_steps():
    plan = build_baseline_verification_plan(
        test_targets=["tests/test_a.py"],
        code_patch_path="/tmp/code.patch",
        test_patch_path="/tmp/test.patch",
    )

    assert plan[0]["step"] == "run_initial_tests"
    assert plan[1]["step"] == "apply_test_patch"
    assert plan[2]["step"] == "run_fail_to_pass_tests"
    assert plan[3]["step"] == "apply_code_patch"
    assert plan[4]["step"] == "run_regression_tests"
