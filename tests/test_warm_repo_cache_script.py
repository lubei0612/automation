from pathlib import Path


def test_warm_repo_cache_script_uses_mirror_clone():
    script = Path("scripts/warm_repo_cache.sh").read_text(encoding="utf-8")
    assert "--mirror" in script
