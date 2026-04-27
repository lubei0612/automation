from dataclasses import dataclass
from pathlib import Path
from typing import List


REQUIRED_FILES = (
    "code.patch",
    "test.patch",
    "Dockerfile",
    "setup_repo.sh",
    "setup_env.sh",
    "run_verification.py",
)


@dataclass(frozen=True)
class PreflightResult:
    valid: bool
    errors: List[str]


def classify_case_inputs(case_dir: Path) -> PreflightResult:
    errors = [
        f"missing required file: {name}"
        for name in REQUIRED_FILES
        if not (case_dir / name).exists()
    ]
    return PreflightResult(valid=not errors, errors=errors)


def inspect_dockerfile(dockerfile: Path) -> PreflightResult:
    text = dockerfile.read_text(encoding="utf-8", errors="replace")
    errors: List[str] = []
    if "WORKDIR /testbed" not in text:
        errors.append("Dockerfile must set WORKDIR /testbed")
    return PreflightResult(valid=not errors, errors=errors)


def extract_test_targets(test_patch: Path) -> List[str]:
    targets: List[str] = []
    for line in test_patch.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("+++ b/tests/"):
            targets.append(line.removeprefix("+++ b/"))
    return targets
