from pathlib import Path

from app.case_materializer import select_output_directory
from app.paths import build_batch_paths


def test_select_output_directory_maps_timeout_bucket(tmp_path: Path):
    paths = build_batch_paths(tmp_path / "batch")

    assert select_output_directory(paths, "timeout") == paths.timeout_dir
