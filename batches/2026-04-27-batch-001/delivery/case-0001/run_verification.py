#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


REPO_DIR = Path("/testbed/eslint")
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_COMMIT = "4e5e9befb95bc1fc7fbcb145825b8e0451e5bc6c"
INSTANCE_ID = "eslint__eslint-10368"


def run(command, cwd=REPO_DIR, check=False):
    return subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, check=check)


def reset_repo():
    run(["git", "reset", "--hard", BASE_COMMIT], check=True)
    run(["git", "clean", "-fd", "--exclude", "node_modules"], check=True)


def apply_patch(name):
    patch_path = SCRIPT_DIR / name
    result = run(["git", "apply", str(patch_path)])
    if result.returncode != 0:
        raise RuntimeError(f"failed to apply {name}: {result.stderr}")


def run_target_tests():
    return run(["./node_modules/.bin/mocha", "tests/lib/rules/prefer-const.js"])


def main():
    results = {
        INSTANCE_ID: {
            "patch_is_None": False,
            "patch_exists": (SCRIPT_DIR / "final.diff").exists(),
            "patch_successfully_applied": False,
            "resolved": False,
            "tests_status": {
                "FAIL_TO_PASS": {"success": [], "failure": []},
                "PASS_TO_PASS": {"success": [], "failure": []},
                "FAIL_TO_FAIL": {"success": [], "failure": []},
                "PASS_TO_FAIL": {"success": [], "failure": []},
            },
        }
    }

    reset_repo()
    apply_patch("test.patch")
    pre = run_target_tests()
    pre_failed = pre.returncode != 0

    reset_repo()
    apply_patch("test.patch")
    apply_patch("final.diff")
    results[INSTANCE_ID]["patch_successfully_applied"] = True
    post = run_target_tests()
    post_passed = post.returncode == 0

    results[INSTANCE_ID]["resolved"] = pre_failed and post_passed
    results[INSTANCE_ID]["tests_status"]["FAIL_TO_PASS"]["failure"] = [] if pre_failed else ["tests/lib/rules/prefer-const.js"]
    results[INSTANCE_ID]["tests_status"]["FAIL_TO_PASS"]["success"] = ["tests/lib/rules/prefer-const.js"] if post_passed else []
    results[INSTANCE_ID]["pre_patch_exit_code"] = pre.returncode
    results[INSTANCE_ID]["post_patch_exit_code"] = post.returncode
    results[INSTANCE_ID]["pre_patch_output"] = pre.stdout + pre.stderr
    results[INSTANCE_ID]["post_patch_output"] = post.stdout + post.stderr

    output_path = SCRIPT_DIR / "results.json"
    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if results[INSTANCE_ID]["resolved"] else 1


if __name__ == "__main__":
    sys.exit(main())
