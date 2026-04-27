from pathlib import Path

from app.metadata import load_case_metadata


def test_load_case_metadata_reads_single_json_file(tmp_path: Path):
    metadata_file = tmp_path / "eslint__eslint-10368.json"
    metadata_file.write_text('{"repo":"eslint/eslint","base_commit":"abc123"}', encoding="utf-8")

    metadata = load_case_metadata(tmp_path)

    assert metadata["repo"] == "eslint/eslint"
    assert metadata["base_commit"] == "abc123"
