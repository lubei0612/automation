from typing import Dict, List


REQUIRED_INSTANCE_FIELDS = (
    "instance_id",
    "repo",
    "base_commit",
    "language",
    "task_category",
    "problem_statement",
    "FAIL_TO_PASS",
    "PASS_TO_PASS",
    "patch",
    "test_patch",
)


def validate_strict_acceptance(
    *,
    final_diff: str,
    instance: Dict,
    trajectory: Dict,
    ignore_model_requirement: bool = False,
) -> List[str]:
    errors: List[str] = []

    if not final_diff.strip():
        errors.append("final_diff_empty")
    elif not final_diff.lstrip().startswith("diff --git "):
        errors.append("final_diff_missing_git_header")

    for field in REQUIRED_INSTANCE_FIELDS:
        value = instance.get(field)
        if value in ("", None, [], {}):
            errors.append(f"instance_missing_{field}")

    if instance.get("patch") != final_diff:
        errors.append("instance_patch_mismatch")

    task_category = instance.get("task_category")
    if task_category and task_category not in {"bug_fix", "feature"}:
        errors.append("instance_invalid_task_category")

    if not isinstance(instance.get("language"), str):
        errors.append("instance_language_not_string")

    metadata = trajectory.get("metadata") or {}
    if not ignore_model_requirement and metadata.get("model") != "claude opus 4.6":
        errors.append("trajectory_model_not_claude_opus_4_6")

    if not metadata.get("agent"):
        errors.append("trajectory_missing_agent")

    git_context = (trajectory.get("instance") or {}).get("git_context") or {}
    if "initial_state" not in git_context:
        errors.append("trajectory_missing_initial_state")
    if git_context.get("final_diff") != final_diff:
        errors.append("trajectory_final_diff_mismatch")

    turn_count = (trajectory.get("metrics") or {}).get("turn_count", 0)
    if turn_count < 5:
        errors.append("trajectory_turn_count_lt_5")

    return errors
