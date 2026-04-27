from pathlib import Path
import zipfile

from app.config import BatchConfig
from app.orchestrator import initialize_batch_workspace


def test_smoke_batch_run_creates_delivery_buckets(tmp_path: Path):
    input_dir = tmp_path / "input_zips"
    output_root = tmp_path / "batches"
    input_dir.mkdir()

    archive = input_dir / "10368.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("10368/Dockerfile", "FROM ubuntu:22.04\nWORKDIR /testbed\n")
        zf.writestr("10368/code.patch", "diff --git a/a b/a\n")
        zf.writestr("10368/test.patch", "diff --git a/tests/test_a.py b/tests/test_a.py\n")
        zf.writestr("10368/setup_repo.sh", "#!/bin/sh\n")
        zf.writestr("10368/setup_env.sh", "#!/bin/sh\n")
        zf.writestr("10368/run_verification.py", "print('ok')\n")

    config = BatchConfig(input_dir=input_dir, output_root=output_root)

    result = initialize_batch_workspace(config, "2026-04-24", 1)

    assert result.batch_id == "2026-04-24-batch-001"
    assert result.paths.accepted_dir.exists()
    assert result.paths.workspace_dir.exists()
    assert len(result.cases) == 1
    assert result.cases[0].source_zip == archive
    assert result.cases[0].extracted_dir.exists()
