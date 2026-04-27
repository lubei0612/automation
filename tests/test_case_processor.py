import json
from pathlib import Path

from app.baseline_verifier import BaselineVerificationResult
from app.case_processor import CaseProcessingContext, process_case
from app.executor import CommandExecutionResult
from app.paths import build_batch_paths


def test_process_case_routes_missing_required_files_to_invalid(tmp_path: Path):
    paths = build_batch_paths(tmp_path / "batch")
    for directory in (
        paths.batch_root,
        paths.accepted_dir,
        paths.unresolved_dir,
        paths.invalid_dir,
        paths.timeout_dir,
        paths.reports_dir,
        paths.workspace_dir,
        paths.manifests_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    extracted_dir = paths.workspace_dir / "case-0001" / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)
    (extracted_dir / "Dockerfile").write_text("FROM ubuntu:22.04\n", encoding="utf-8")

    context = CaseProcessingContext(
        case_id="case-0001",
        source_zip=tmp_path / "case.zip",
        extracted_dir=extracted_dir,
        paths=paths,
    )

    result = process_case(context)

    assert result.classification == "invalid"
    assert (paths.invalid_dir / "case-0001" / "acceptance_report.json").exists()
    assert (paths.manifests_dir / "case-0001.json").exists()


def test_process_case_can_materialize_accepted_case_with_injected_builder(tmp_path: Path):
    paths = build_batch_paths(tmp_path / "batch")
    for directory in (
        paths.batch_root,
        paths.accepted_dir,
        paths.unresolved_dir,
        paths.invalid_dir,
        paths.timeout_dir,
        paths.reports_dir,
        paths.workspace_dir,
        paths.manifests_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    extracted_dir = paths.workspace_dir / "case-0002" / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)
    for filename in (
        "Dockerfile",
        "code.patch",
        "test.patch",
        "setup_repo.sh",
        "setup_env.sh",
        "run_verification.py",
    ):
        (extracted_dir / filename).write_text("x\n", encoding="utf-8")
    (extracted_dir / "meta.json").write_text(
        json.dumps({"repo": "eslint/eslint", "base_commit": "abc123"}),
        encoding="utf-8",
    )

    context = CaseProcessingContext(
        case_id="case-0002",
        source_zip=tmp_path / "case2.zip",
        extracted_dir=extracted_dir,
        paths=paths,
    )

    def artifact_builder(case_context):
        return {
            "classification": "accepted",
            "files": {
                "final.diff": "diff --git a/a b/a\n",
                "instance.json": {"instance_id": case_context.case_id},
                "trajectory.json": {"instance_id": case_context.case_id},
                "acceptance_report.json": {"accepted": True},
            },
        }

    result = process_case(context, artifact_builder=artifact_builder)

    assert result.classification == "accepted"
    assert (paths.accepted_dir / "case-0002" / "final.diff").exists()
    manifest = json.loads((paths.manifests_dir / "case-0002.json").read_text(encoding="utf-8"))
    assert manifest["classification"] == "accepted"


def test_process_case_routes_baseline_failure_to_invalid(tmp_path: Path):
    paths = build_batch_paths(tmp_path / "batch")
    for directory in (
        paths.batch_root,
        paths.accepted_dir,
        paths.unresolved_dir,
        paths.invalid_dir,
        paths.timeout_dir,
        paths.reports_dir,
        paths.workspace_dir,
        paths.manifests_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    extracted_dir = paths.workspace_dir / "case-0003" / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)
    for filename in (
        "Dockerfile",
        "code.patch",
        "test.patch",
        "setup_repo.sh",
        "setup_env.sh",
        "run_verification.py",
    ):
        (extracted_dir / filename).write_text("x\n", encoding="utf-8")
    (extracted_dir / "meta.json").write_text(
        json.dumps({"repo": "eslint/eslint", "base_commit": "abc123"}),
        encoding="utf-8",
    )

    context = CaseProcessingContext(
        case_id="case-0003",
        source_zip=tmp_path / "case3.zip",
        extracted_dir=extracted_dir,
        paths=paths,
    )

    def fake_baseline_verifier(**kwargs):
        return BaselineVerificationResult(
            valid=False,
            failed_step="setup_repo",
            executions=[
                CommandExecutionResult(
                    command=["bash", "setup_repo.sh"],
                    exit_code=7,
                    stdout="",
                    stderr="curl: (35) Recv failure",
                    timed_out=False,
                )
            ],
        )

    result = process_case(context, baseline_verifier=fake_baseline_verifier)

    assert result.classification == "invalid"
    manifest = json.loads((paths.manifests_dir / "case-0003.json").read_text(encoding="utf-8"))
    assert manifest["state"] == "INVALID"
    acceptance = json.loads((paths.invalid_dir / "case-0003" / "acceptance_report.json").read_text(encoding="utf-8"))
    assert acceptance["baseline_failed_step"] == "setup_repo"
    assert acceptance["baseline_exit_code"] == 7
    assert acceptance["baseline_timed_out"] is False
    assert acceptance["baseline_stderr"] == "curl: (35) Recv failure"


def test_process_case_routes_runtime_failure_to_unresolved(tmp_path: Path):
    paths = build_batch_paths(tmp_path / "batch")
    for directory in (
        paths.batch_root,
        paths.accepted_dir,
        paths.unresolved_dir,
        paths.invalid_dir,
        paths.timeout_dir,
        paths.reports_dir,
        paths.workspace_dir,
        paths.manifests_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    extracted_dir = paths.workspace_dir / "case-0004" / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)
    for filename in (
        "Dockerfile",
        "code.patch",
        "test.patch",
        "setup_repo.sh",
        "setup_env.sh",
        "run_verification.py",
    ):
        (extracted_dir / filename).write_text("x\n", encoding="utf-8")
    (extracted_dir / "meta.json").write_text(
        json.dumps({"repo": "eslint/eslint", "base_commit": "abc123"}),
        encoding="utf-8",
    )

    context = CaseProcessingContext(
        case_id="case-0004",
        source_zip=tmp_path / "case4.zip",
        extracted_dir=extracted_dir,
        paths=paths,
    )

    def fake_baseline_verifier(**kwargs):
        return BaselineVerificationResult(valid=True, failed_step=None, executions=[])

    def fake_codex_runtime(**kwargs):
        return CommandExecutionResult(
            command=["codex", "exec"],
            exit_code=1,
            stdout="",
            stderr="failed",
            timed_out=False,
        )

    result = process_case(
        context,
        baseline_verifier=fake_baseline_verifier,
        codex_runtime=fake_codex_runtime,
    )

    assert result.classification == "unresolved"
    acceptance = json.loads((paths.unresolved_dir / "case-0004" / "acceptance_report.json").read_text(encoding="utf-8"))
    assert acceptance["runtime_exit_code"] == 1
    assert acceptance["runtime_timed_out"] is False
    assert acceptance["runtime_stderr"] == "failed"


def test_process_case_routes_runtime_success_without_required_metadata_to_unresolved(tmp_path: Path):
    paths = build_batch_paths(tmp_path / "batch")
    for directory in (
        paths.batch_root,
        paths.accepted_dir,
        paths.unresolved_dir,
        paths.invalid_dir,
        paths.timeout_dir,
        paths.reports_dir,
        paths.workspace_dir,
        paths.manifests_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    extracted_dir = paths.workspace_dir / "case-0005" / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)
    for filename in (
        "Dockerfile",
        "code.patch",
        "test.patch",
        "setup_repo.sh",
        "setup_env.sh",
        "run_verification.py",
    ):
        (extracted_dir / filename).write_text("x\n", encoding="utf-8")
    (extracted_dir / "meta.json").write_text(
        json.dumps({"repo": "eslint/eslint", "base_commit": "abc123"}),
        encoding="utf-8",
    )

    context = CaseProcessingContext(
        case_id="case-0005",
        source_zip=tmp_path / "case5.zip",
        extracted_dir=extracted_dir,
        paths=paths,
    )

    def fake_baseline_verifier(**kwargs):
        return BaselineVerificationResult(valid=True, failed_step=None, executions=[])

    def fake_codex_runtime(**kwargs):
        return CommandExecutionResult(
            command=["codex", "exec"],
            exit_code=0,
            stdout="done",
            stderr="",
            timed_out=False,
        )

    def fake_capture_diff(workspace, executor=None, timeout_seconds=30.0):
        return "diff --git a/a b/a\n"

    result = process_case(
        context,
        baseline_verifier=fake_baseline_verifier,
        codex_runtime=fake_codex_runtime,
        final_diff_capturer=fake_capture_diff,
    )

    assert result.classification == "unresolved"
    assert (paths.unresolved_dir / "case-0005" / "final.diff").exists()
    acceptance = json.loads((paths.unresolved_dir / "case-0005" / "acceptance_report.json").read_text(encoding="utf-8"))
    assert "strict_acceptance" in acceptance["failed_gates"]
    assert "instance_missing_language" in acceptance["strict_acceptance_errors"]


def test_process_case_routes_runtime_success_with_empty_diff_to_unresolved(tmp_path: Path):
    paths = build_batch_paths(tmp_path / "batch")
    for directory in (
        paths.batch_root,
        paths.accepted_dir,
        paths.unresolved_dir,
        paths.invalid_dir,
        paths.timeout_dir,
        paths.reports_dir,
        paths.workspace_dir,
        paths.manifests_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    extracted_dir = paths.workspace_dir / "case-0006" / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)
    for filename in (
        "Dockerfile",
        "code.patch",
        "test.patch",
        "setup_repo.sh",
        "setup_env.sh",
        "run_verification.py",
    ):
        (extracted_dir / filename).write_text("x\n", encoding="utf-8")
    (extracted_dir / "meta.json").write_text(
        json.dumps(
            {
                "repo": "eslint/eslint",
                "base_commit": "abc123",
                "language": "JavaScript",
                "task_category": "bug_fix",
                "problem_statement": "Fix issue",
                "FAIL_TO_PASS": ["tests/lib/rules/prefer-const.js"],
                "PASS_TO_PASS": ["tests/lib/rules/no-unused-vars.js"],
            }
        ),
        encoding="utf-8",
    )

    context = CaseProcessingContext(
        case_id="case-0006",
        source_zip=tmp_path / "case6.zip",
        extracted_dir=extracted_dir,
        paths=paths,
    )

    def fake_baseline_verifier(**kwargs):
        return BaselineVerificationResult(valid=True, failed_step=None, executions=[])

    def fake_codex_runtime(**kwargs):
        return CommandExecutionResult(
            command=["codex", "exec"],
            exit_code=0,
            stdout="done",
            stderr="",
            timed_out=False,
        )

    def fake_capture_diff(workspace, executor=None, timeout_seconds=30.0):
        return ""

    result = process_case(
        context,
        baseline_verifier=fake_baseline_verifier,
        codex_runtime=fake_codex_runtime,
        final_diff_capturer=fake_capture_diff,
    )

    assert result.classification == "unresolved"
    acceptance = json.loads((paths.unresolved_dir / "case-0006" / "acceptance_report.json").read_text(encoding="utf-8"))
    assert "strict_acceptance" in acceptance["failed_gates"]
    assert "final_diff_empty" in acceptance["strict_acceptance_errors"]
