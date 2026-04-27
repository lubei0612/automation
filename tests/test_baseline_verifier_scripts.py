from pathlib import Path

from app.baseline_verifier import build_script_based_verification_commands


def test_build_script_based_verification_commands_uses_setup_and_verification(tmp_path: Path):
    (tmp_path / "setup_repo.sh").write_text("mkdir -p /testbed\n", encoding="utf-8")
    (tmp_path / "setup_env.sh").write_text("echo ok\n", encoding="utf-8")
    (tmp_path / "run_verification.py").write_text('REPO_PATH = "/testbed/eslint"\n', encoding="utf-8")

    commands = build_script_based_verification_commands(
        case_dir=tmp_path,
        repo_path="/testbed/eslint",
    )

    assert commands[0][0:2] == ["bash", str((tmp_path / ".runtime" / "setup_repo.sh").resolve())]
    assert commands[1][0:2] == ["bash", str((tmp_path / ".runtime" / "setup_env.sh").resolve())]
    assert commands[2][0:2] == ["python3", str((tmp_path / ".runtime" / "run_verification.py").resolve())]


def test_build_script_based_verification_commands_can_use_repo_cache(tmp_path: Path):
    (tmp_path / "setup_repo.sh").write_text(
        "git clone https://github.com/eslint/eslint.git /testbed/eslint\n",
        encoding="utf-8",
    )
    (tmp_path / "setup_env.sh").write_text("echo ok\n", encoding="utf-8")
    (tmp_path / "run_verification.py").write_text('REPO_PATH = "/testbed/eslint"\n', encoding="utf-8")
    repo_cache_root = tmp_path / "repo_cache"
    (repo_cache_root / "eslint__eslint").mkdir(parents=True)

    commands = build_script_based_verification_commands(
        case_dir=tmp_path,
        repo_path="/testbed/eslint",
        repo_cache_root=repo_cache_root,
    )

    rewritten = (tmp_path / ".runtime" / "setup_repo.sh").read_text(encoding="utf-8")
    assert str(repo_cache_root / "eslint__eslint") in rewritten


def test_build_script_based_verification_commands_adds_archive_fallback_when_cache_missing(tmp_path: Path):
    (tmp_path / "setup_repo.sh").write_text(
        "\n".join(
            [
                "git clone https://github.com/eslint/eslint.git /testbed/eslint",
                "cd /testbed/eslint",
                "git checkout 4e5e9befb95bc1fc7fbcb145825b8e0451e5bc6c",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "setup_env.sh").write_text("echo ok\n", encoding="utf-8")
    (tmp_path / "run_verification.py").write_text('REPO_PATH = "/testbed/eslint"\n', encoding="utf-8")
    repo_cache_root = tmp_path / "repo_cache"
    repo_cache_root.mkdir(parents=True)

    build_script_based_verification_commands(
        case_dir=tmp_path,
        repo_path="/testbed/eslint",
        repo_cache_root=repo_cache_root,
    )

    rewritten = (tmp_path / ".runtime" / "setup_repo.sh").read_text(encoding="utf-8")
    assert "codex_clone_or_restore_repo" in rewritten
