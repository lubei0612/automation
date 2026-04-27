from pathlib import Path


def test_repo_cache_readme_exists():
    readme = Path("repo_cache/README.md")
    assert readme.exists()
