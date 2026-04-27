from pathlib import Path

from app.preflight import inspect_dockerfile


def test_inspect_dockerfile_detects_missing_testbed_workdir(tmp_path: Path):
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM ubuntu:22.04\n", encoding="utf-8")

    result = inspect_dockerfile(dockerfile)

    assert result.valid is False
    assert "WORKDIR /testbed" in result.errors[0]
