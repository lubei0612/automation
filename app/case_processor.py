from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional

from app.artifacts import build_acceptance_report
from app.baseline_verifier import verify_baseline
from app.codex_runtime import run_codex_task
from app.git_tools import capture_final_diff
from app.manifest_store import write_case_manifest
from app.metadata import load_case_metadata
from app.persistence import materialize_case_output
from app.preflight import classify_case_inputs, extract_test_targets
from app.state_machine import CaseState
from app.strict_acceptance import validate_strict_acceptance
from app.trajectory_builder import build_trajectory_record
from app.artifacts import build_instance_record


@dataclass(frozen=True)
class CaseProcessingContext:
    case_id: str
    source_zip: Path
    extracted_dir: Path
    paths: any


@dataclass(frozen=True)
class CaseProcessingResult:
    case_id: str
    state: CaseState
    classification: str


def _source_bundle_payload(context: CaseProcessingContext) -> Dict[str, str]:
    return {
        "case_id": context.case_id,
        "source_zip_name": context.source_zip.name,
        "source_zip_path": str(context.source_zip.resolve()),
    }


def _default_artifact_builder(case_context: CaseProcessingContext, metadata: Dict) -> Dict:
    report = build_acceptance_report(
        case_id=case_context.case_id,
        accepted=False,
        classification="unresolved",
        failed_gates=["runtime_not_implemented"],
    )
    return {
        "classification": "unresolved",
        "files": {
            "acceptance_report.json": report,
            "source_bundle.json": _source_bundle_payload(case_context),
        },
    }


def process_case(
    context: CaseProcessingContext,
    artifact_builder: Optional[Callable[[CaseProcessingContext], Dict]] = None,
    baseline_verifier: Callable[..., object] = verify_baseline,
    codex_runtime: Callable[..., object] = run_codex_task,
    final_diff_capturer: Callable[..., str] = capture_final_diff,
) -> CaseProcessingResult:
    manifest_path = context.paths.manifests_dir / f"{context.case_id}.json"
    preflight = classify_case_inputs(context.extracted_dir)
    if not preflight.valid:
        report = build_acceptance_report(
            case_id=context.case_id,
            accepted=False,
            classification="invalid",
            failed_gates=["preflight"],
        )
        materialize_case_output(
            paths=context.paths,
            classification="invalid",
            case_id=context.case_id,
            files={
                "acceptance_report.json": report,
                "source_bundle.json": _source_bundle_payload(context),
            },
        )
        write_case_manifest(
            manifest_path,
            {
                "case_id": context.case_id,
                "state": CaseState.INVALID.value,
                "classification": "invalid",
            },
        )
        return CaseProcessingResult(
            case_id=context.case_id,
            state=CaseState.INVALID,
            classification="invalid",
        )

    metadata = load_case_metadata(context.extracted_dir)
    if artifact_builder is None:
        baseline_result = baseline_verifier(
            workspace=context.extracted_dir,
            test_targets=extract_test_targets(context.extracted_dir / "test.patch"),
            code_patch_path=str(context.extracted_dir / "code.patch"),
            test_patch_path=str(context.extracted_dir / "test.patch"),
        )
        if not baseline_result.valid:
            failed_execution = baseline_result.executions[-1] if baseline_result.executions else None
            report = build_acceptance_report(
                case_id=context.case_id,
                accepted=False,
                classification="invalid",
                failed_gates=["baseline_verification"],
            )
            report.update(
                {
                    "baseline_failed_step": baseline_result.failed_step,
                    "baseline_exit_code": None if failed_execution is None else failed_execution.exit_code,
                    "baseline_timed_out": False if failed_execution is None else failed_execution.timed_out,
                    "baseline_stdout": "" if failed_execution is None else failed_execution.stdout,
                    "baseline_stderr": "" if failed_execution is None else failed_execution.stderr,
                }
            )
            materialize_case_output(
                paths=context.paths,
                classification="invalid",
                case_id=context.case_id,
                files={
                    "acceptance_report.json": report,
                    "source_bundle.json": _source_bundle_payload(context),
                },
            )
            write_case_manifest(
                manifest_path,
                {
                    "case_id": context.case_id,
                    "state": CaseState.INVALID.value,
                    "classification": "invalid",
                },
            )
            return CaseProcessingResult(
                case_id=context.case_id,
                state=CaseState.INVALID,
                classification="invalid",
            )

        runtime_result = codex_runtime(
            prompt=f"Resolve task for {context.case_id}",
            workspace=context.extracted_dir,
            model_name=None,
        )
        if runtime_result.exit_code != 0 or runtime_result.timed_out:
            report = build_acceptance_report(
                case_id=context.case_id,
                accepted=False,
                classification="unresolved",
                failed_gates=["agent_runtime"],
            )
            report.update(
                {
                    "runtime_exit_code": runtime_result.exit_code,
                    "runtime_timed_out": runtime_result.timed_out,
                    "runtime_stdout": runtime_result.stdout,
                    "runtime_stderr": runtime_result.stderr,
                }
            )
            built = {
                "classification": "unresolved",
                "files": {
                    "acceptance_report.json": report,
                    "source_bundle.json": _source_bundle_payload(context),
                },
            }
        else:
            final_diff = final_diff_capturer(context.extracted_dir)
            instance_record = build_instance_record(
                instance_id=context.case_id,
                repo=metadata.get("repo", ""),
                base_commit=metadata.get("base_commit", ""),
                language=metadata.get("language", ""),
                task_category=metadata.get("task_category", ""),
                problem_statement=metadata.get("problem_statement", ""),
                fail_to_pass=metadata.get("FAIL_TO_PASS", []),
                pass_to_pass=metadata.get("PASS_TO_PASS", []),
                patch=final_diff,
                test_patch=(context.extracted_dir / "test.patch").read_text(encoding="utf-8", errors="replace"),
            )
            trajectory_record = build_trajectory_record(
                instance_id=context.case_id,
                instruction=f"Resolve task for {context.case_id}",
                instance={"repo": metadata.get("repo", ""), "base_commit": metadata.get("base_commit", "")},
                metadata={"agent": "codex", "model": "configured-at-runtime"},
                trajectory=[
                    {"role": "user", "content": "Resolve task"},
                    {"role": "assistant", "content": runtime_result.stdout},
                ],
            )
            strict_errors = validate_strict_acceptance(
                final_diff=final_diff,
                instance=instance_record,
                trajectory=trajectory_record,
            )
            if strict_errors:
                report = build_acceptance_report(
                    case_id=context.case_id,
                    accepted=False,
                    classification="unresolved",
                    failed_gates=["strict_acceptance"],
                )
                report["strict_acceptance_errors"] = strict_errors
                built = {
                    "classification": "unresolved",
                    "files": {
                        "final.diff": final_diff,
                        "instance.json": instance_record,
                        "trajectory.json": trajectory_record,
                        "acceptance_report.json": report,
                        "source_bundle.json": _source_bundle_payload(context),
                    },
                }
            else:
                built = {
                    "classification": "accepted",
                    "files": {
                        "final.diff": final_diff,
                        "instance.json": instance_record,
                        "trajectory.json": trajectory_record,
                        "acceptance_report.json": build_acceptance_report(
                            case_id=context.case_id,
                            accepted=True,
                            classification="accepted",
                            failed_gates=[],
                        ),
                        "source_bundle.json": _source_bundle_payload(context),
                    },
                }
    else:
        builder = artifact_builder or (lambda case_context: _default_artifact_builder(case_context, metadata))
        built = builder(context)
    classification = built["classification"]
    materialize_case_output(
        paths=context.paths,
        classification=classification,
        case_id=context.case_id,
        files=built["files"],
    )

    state = CaseState.ACCEPTED if classification == "accepted" else CaseState.UNRESOLVED
    write_case_manifest(
        manifest_path,
        {
            "case_id": context.case_id,
            "state": state.value,
            "classification": classification,
        },
    )
    return CaseProcessingResult(
        case_id=context.case_id,
        state=state,
        classification=classification,
    )
