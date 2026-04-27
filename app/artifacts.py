from typing import Dict, List


def build_instance_record(
    *,
    instance_id: str,
    repo: str,
    base_commit: str,
    language: str,
    task_category: str,
    problem_statement: str,
    fail_to_pass: List[str],
    pass_to_pass: List[str],
    patch: str,
    test_patch: str,
) -> Dict:
    return {
        "instance_id": instance_id,
        "repo": repo,
        "base_commit": base_commit,
        "language": language,
        "task_category": task_category,
        "problem_statement": problem_statement,
        "FAIL_TO_PASS": fail_to_pass,
        "PASS_TO_PASS": pass_to_pass,
        "patch": patch,
        "test_patch": test_patch,
    }


def build_acceptance_report(
    *,
    case_id: str,
    accepted: bool,
    classification: str,
    failed_gates: List[str],
) -> Dict:
    return {
        "case_id": case_id,
        "accepted": accepted,
        "classification": classification,
        "failed_gates": failed_gates,
    }
