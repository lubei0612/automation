from pathlib import Path
import zipfile

from app.extraction import extract_zip_to_directory


def test_extract_zip_to_directory_unpacks_contents(tmp_path: Path):
    archive = tmp_path / "case.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("10368/Dockerfile", "FROM ubuntu:22.04\n")

    output_dir = tmp_path / "extracted"
    extract_zip_to_directory(archive, output_dir)

    assert (output_dir / "10368" / "Dockerfile").read_text(encoding="utf-8") == "FROM ubuntu:22.04\n"


def test_extract_zip_to_directory_clears_existing_output(tmp_path: Path):
    archive = tmp_path / "case.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("fresh.txt", "ok")

    output_dir = tmp_path / "extracted"
    output_dir.mkdir()
    (output_dir / ".runtime").mkdir()
    (output_dir / ".runtime" / "stale.txt").write_text("stale", encoding="utf-8")

    extract_zip_to_directory(archive, output_dir)

    assert (output_dir / "fresh.txt").read_text(encoding="utf-8") == "ok"
    assert not (output_dir / ".runtime" / "stale.txt").exists()
