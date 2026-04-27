import json
from pathlib import Path

from app.persistence import materialize_case_output
from app.paths import build_batch_paths


def test_materialize_case_output_writes_case_bundle(tmp_path: Path):
    paths = build_batch_paths(tmp_path / "2026-04-24-batch-001")
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

    materialize_case_output(
        paths=paths,
        classification="accepted",
        case_id="case-0001",
        files={
            "final.diff": "diff --git a/a b/a\n",
            "instance.json": {"instance_id": "case-0001"},
            "trajectory.json": {"instance_id": "case-0001"},
            "acceptance_report.json": {"accepted": True},
        },
    )

    case_dir = paths.accepted_dir / "case-0001"
    assert (case_dir / "final.diff").read_text(encoding="utf-8") == "diff --git a/a b/a\n"
    assert json.loads((case_dir / "instance.json").read_text(encoding="utf-8"))["instance_id"] == "case-0001"


def test_materialize_case_output_copies_accepted_bundle_to_delivery(tmp_path: Path):
    paths = build_batch_paths(tmp_path / "2026-04-24-batch-001")
    for directory in (
        paths.batch_root,
        paths.delivery_dir,
        paths.accepted_dir,
        paths.unresolved_dir,
        paths.invalid_dir,
        paths.timeout_dir,
        paths.reports_dir,
        paths.workspace_dir,
        paths.manifests_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    materialize_case_output(
        paths=paths,
        classification="accepted",
        case_id="case-0001",
        files={"acceptance_report.json": {"accepted": True}},
    )

    assert (paths.delivery_dir / "case-0001" / "acceptance_report.json").exists()
