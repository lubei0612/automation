from pathlib import Path

from app.main import build_default_config


def test_build_default_config_prefers_repo_cache_directory(tmp_path: Path):
    config = build_default_config(tmp_path)
    assert config.repo_cache_root == tmp_path / "repo_cache"
