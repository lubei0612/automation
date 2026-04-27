from pathlib import Path

from app.repo_setup import extract_repo_path_from_setup_repo


def test_extract_repo_path_from_setup_repo_reads_git_clone_target(tmp_path: Path):
    script = tmp_path / "setup_repo.sh"
    script.write_text(
        "#!/bin/bash\n"
        "git clone https://github.com/eslint/eslint.git /testbed/eslint\n",
        encoding="utf-8",
    )

    assert extract_repo_path_from_setup_repo(script) == "/testbed/eslint"
