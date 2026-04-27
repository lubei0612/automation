from app.strict_acceptance import validate_strict_acceptance


def _valid_instance(final_diff: str):
    return {
        "instance_id": "eslint__eslint-10368",
        "repo": "eslint/eslint",
        "base_commit": "abc123",
        "language": "JavaScript",
        "task_category": "bug_fix",
        "problem_statement": "Fix prefer-const false positive",
        "FAIL_TO_PASS": ["tests/lib/rules/prefer-const.js"],
        "PASS_TO_PASS": ["tests/lib/rules/prefer-const.js"],
        "patch": final_diff,
        "test_patch": "diff --git a/tests/a.js b/tests/a.js\n",
    }


def _valid_trajectory(final_diff: str, model: str):
    return {
        "metadata": {"agent": "codex", "model": model},
        "instance": {
            "git_context": {
                "initial_state": {"lib/rules/prefer-const.js": "\"use strict\";\n"},
                "final_diff": final_diff,
            }
        },
        "metrics": {"turn_count": 5},
    }


def test_strict_acceptance_can_ignore_model_requirement_only():
    final_diff = "diff --git a/lib/rules/prefer-const.js b/lib/rules/prefer-const.js\n"
    errors = validate_strict_acceptance(
        final_diff=final_diff,
        instance=_valid_instance(final_diff),
        trajectory=_valid_trajectory(final_diff, "gpt-5-codex"),
        ignore_model_requirement=True,
    )

    assert errors == []
