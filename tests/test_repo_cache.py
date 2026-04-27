from pathlib import Path

from app.repo_cache import build_cached_clone_replacement, parse_github_clone


def test_parse_github_clone_extracts_repo_owner_name_and_target():
    line = "git clone https://github.com/eslint/eslint.git /testbed/eslint"
    parsed = parse_github_clone(line)

    assert parsed == {
        "owner": "eslint",
        "repo": "eslint",
        "target": "/testbed/eslint",
    }


def test_build_cached_clone_replacement_points_to_local_cache(tmp_path: Path):
    replacement = build_cached_clone_replacement(
        owner="eslint",
        repo="eslint",
        target="/tmp/testbed/eslint",
        repo_cache_root=tmp_path,
    )

    assert str(tmp_path / "eslint__eslint") in replacement
    assert replacement.endswith(" /tmp/testbed/eslint")
