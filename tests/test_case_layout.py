from pathlib import Path

from app.case_layout import resolve_case_root


def test_resolve_case_root_uses_single_nested_directory_when_present(tmp_path: Path):
    extracted = tmp_path / "extracted"
    nested = extracted / "10368"
    nested.mkdir(parents=True)
    (nested / "Dockerfile").write_text("FROM ubuntu:22.04\n", encoding="utf-8")

    assert resolve_case_root(extracted) == nested


def test_resolve_case_root_keeps_root_when_files_exist_at_top_level(tmp_path: Path):
    extracted = tmp_path / "extracted"
    extracted.mkdir(parents=True)
    (extracted / "Dockerfile").write_text("FROM ubuntu:22.04\n", encoding="utf-8")

    assert resolve_case_root(extracted) == extracted
