import json
from pathlib import Path

from app.batch_runner import BatchCase, run_batch
from app.paths import build_batch_paths


def test_run_batch_aggregates_case_results_and_writes_summary(tmp_path: Path):
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

    cases = [
        BatchCase(case_id="case-0001", source_zip=tmp_path / "a.zip", extracted_dir=tmp_path / "a"),
        BatchCase(case_id="case-0002", source_zip=tmp_path / "b.zip", extracted_dir=tmp_path / "b"),
    ]

    def fake_processor(case):
        if case.case_id == "case-0001":
            return {"classification": "accepted"}
        return {"classification": "invalid"}

    metrics = run_batch(cases=cases, paths=paths, processor=fake_processor)

    assert metrics.accepted == 1
    assert metrics.invalid == 1
    summary = json.loads((paths.reports_dir / "batch_summary.json").read_text(encoding="utf-8"))
    assert summary["accepted"] == 1
    assert summary["invalid"] == 1
    assert summary["case_concurrency"] == 1
    assert summary["delivery_dir"] == str(paths.delivery_dir)
    delivery_manifest = json.loads((paths.reports_dir / "delivery_manifest.json").read_text(encoding="utf-8"))
    failure_manifest = json.loads((paths.reports_dir / "failure_manifest.json").read_text(encoding="utf-8"))
    assert delivery_manifest["accepted_count"] == 1
    assert delivery_manifest["items"][0]["case_id"] == "case-0001"
    assert failure_manifest["failed_count"] == 1
    assert failure_manifest["items"][0]["case_id"] == "case-0002"
    assert failure_manifest["items"][0]["classification"] == "invalid"


def test_run_batch_writes_failures_csv_and_markdown_summary(tmp_path: Path):
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

    cases = [
        BatchCase(case_id="case-0001", source_zip=tmp_path / "a.zip", extracted_dir=tmp_path / "a"),
        BatchCase(case_id="case-0002", source_zip=tmp_path / "b.zip", extracted_dir=tmp_path / "b"),
    ]

    def fake_processor(case):
        if case.case_id == "case-0001":
            return {"classification": "timeout"}
        return {"classification": "accepted"}

    run_batch(cases=cases, paths=paths, processor=fake_processor)

    failures_csv = (paths.reports_dir / "failures.csv").read_text(encoding="utf-8")
    summary_md = (paths.reports_dir / "batch_summary.md").read_text(encoding="utf-8")

    assert "case_id,classification" in failures_csv
    assert "case-0001,timeout" in failures_csv
    assert "Accepted: 1" in summary_md
    assert "Timeout: 1" in summary_md


def test_run_batch_supports_parallel_worker_count(tmp_path: Path):
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

    cases = [
        BatchCase(case_id="case-0001", source_zip=tmp_path / "a.zip", extracted_dir=tmp_path / "a"),
        BatchCase(case_id="case-0002", source_zip=tmp_path / "b.zip", extracted_dir=tmp_path / "b"),
        BatchCase(case_id="case-0003", source_zip=tmp_path / "c.zip", extracted_dir=tmp_path / "c"),
    ]

    def fake_processor(case):
        return {"classification": "accepted"}

    metrics = run_batch(cases=cases, paths=paths, processor=fake_processor, max_workers=2)

    assert metrics.accepted == 3
