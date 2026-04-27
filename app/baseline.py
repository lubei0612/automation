from typing import Dict, List


def build_baseline_verification_plan(
    *,
    test_targets: List[str],
    code_patch_path: str,
    test_patch_path: str,
) -> List[Dict]:
    return [
        {"step": "run_initial_tests", "targets": test_targets},
        {"step": "apply_test_patch", "patch": test_patch_path},
        {"step": "run_fail_to_pass_tests", "targets": test_targets},
        {"step": "apply_code_patch", "patch": code_patch_path},
        {"step": "run_regression_tests", "targets": test_targets},
    ]
