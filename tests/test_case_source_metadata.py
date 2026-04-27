import json
from pathlib import Path

from app.case_processor import CaseProcessingContext, process_case
from app.paths import build_batch_paths


def test_process_case_writes_source_zip_metadata_for_failed_case(tmp_path: Path):
    paths = build_batch_paths(tmp_path / "batch")
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

    extracted_dir = paths.workspace_dir / "case-0001" / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)
    source_zip = tmp_path / "10368(1).zip"
    source_zip.write_text("zip", encoding="utf-8")
    (extracted_dir / "Dockerfile").write_text("FROM ubuntu:22.04\n", encoding="utf-8")

    context = CaseProcessingContext(
        case_id="case-0001",
        source_zip=source_zip,
        extracted_dir=extracted_dir,
        paths=paths,
    )

    result = process_case(context)

    assert result.classification == "invalid"
    metadata = json.loads((paths.invalid_dir / "case-0001" / "source_bundle.json").read_text(encoding="utf-8"))
    assert metadata["source_zip_name"] == "10368(1).zip"
    assert metadata["source_zip_path"].endswith("10368(1).zip")
