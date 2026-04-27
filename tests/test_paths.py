from pathlib import Path

from app.paths import build_batch_paths


def test_build_batch_paths_includes_delivery_directory(tmp_path: Path):
    paths = build_batch_paths(tmp_path / "batch")

    assert paths.delivery_dir == tmp_path / "batch" / "delivery"
