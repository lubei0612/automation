from pathlib import Path

from app.preflight import classify_case_inputs


def test_preflight_marks_missing_test_patch_invalid(tmp_path: Path):
    (tmp_path / "Dockerfile").write_text("FROM ubuntu:22.04\n", encoding="utf-8")

    result = classify_case_inputs(tmp_path)

    assert result.valid is False
    assert any("test.patch" in error for error in result.errors)
