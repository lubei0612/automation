from pathlib import Path

from app.discovery import discover_zip_inputs


def test_discover_zip_inputs_only_returns_zip_files(tmp_path: Path):
    (tmp_path / "a.zip").write_bytes(b"PK")
    (tmp_path / "b.txt").write_text("ignore", encoding="utf-8")
    (tmp_path / "c.zip").write_bytes(b"PK")

    names = [path.name for path in discover_zip_inputs(tmp_path)]

    assert names == ["a.zip", "c.zip"]
