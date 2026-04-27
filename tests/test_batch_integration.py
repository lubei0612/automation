from pathlib import Path

from app.batch_runner import BatchCase, run_initialized_batch
from app.orchestrator import BatchWorkspace, CaseWorkspace
from app.paths import build_batch_paths


def test_run_initialized_batch_processes_workspace_cases(tmp_path: Path):
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

    workspace = BatchWorkspace(
        batch_id="2026-04-24-batch-001",
        paths=paths,
        cases=[
            CaseWorkspace(source_zip=tmp_path / "a.zip", extracted_dir=tmp_path / "case-0001"),
            CaseWorkspace(source_zip=tmp_path / "b.zip", extracted_dir=tmp_path / "case-0002"),
        ],
    )

    seen = []

    def fake_processor(case):
        seen.append(case.case_id)
        return {"classification": "accepted"}

    metrics = run_initialized_batch(workspace=workspace, processor=fake_processor)

    assert metrics.accepted == 2
    assert seen == ["case-0001", "case-0002"]
