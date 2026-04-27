from pathlib import Path

from app.local_runtime import prepare_local_runtime_scripts


def test_prepare_local_runtime_scripts_rewrites_testbed_paths(tmp_path: Path):
    case_dir = tmp_path / "case"
    case_dir.mkdir()
    (case_dir / "setup_repo.sh").write_text("mkdir -p /testbed\n", encoding="utf-8")
    (case_dir / "setup_env.sh").write_text("echo ok\n", encoding="utf-8")
    (case_dir / "run_verification.py").write_text('REPO_PATH = "/testbed/eslint"\n', encoding="utf-8")

    runtime = prepare_local_runtime_scripts(case_dir)

    rewritten_repo = runtime.runtime_dir / "setup_repo.sh"
    rewritten_verify = runtime.runtime_dir / "run_verification.py"
    assert str(runtime.testbed_root) in rewritten_repo.read_text(encoding="utf-8")
    assert str(runtime.testbed_root / "eslint") in rewritten_verify.read_text(encoding="utf-8")


def test_prepare_local_runtime_scripts_rewrites_git_clone_to_cache_when_available(tmp_path: Path):
    case_dir = tmp_path / "case"
    case_dir.mkdir()
    (case_dir / "setup_repo.sh").write_text(
        "git clone https://github.com/eslint/eslint.git /testbed/eslint\n",
        encoding="utf-8",
    )
    (case_dir / "setup_env.sh").write_text("echo ok\n", encoding="utf-8")
    (case_dir / "run_verification.py").write_text('REPO_PATH = "/testbed/eslint"\n', encoding="utf-8")

    repo_cache_root = tmp_path / "repo_cache"
    (repo_cache_root / "eslint__eslint").mkdir(parents=True)

    runtime = prepare_local_runtime_scripts(case_dir, repo_cache_root=repo_cache_root)

    rewritten_repo = runtime.runtime_dir / "setup_repo.sh"
    assert str(repo_cache_root / "eslint__eslint") in rewritten_repo.read_text(encoding="utf-8")


def test_prepare_local_runtime_scripts_adds_archive_fallback_for_github_clone(tmp_path: Path):
    case_dir = tmp_path / "case"
    case_dir.mkdir()
    (case_dir / "setup_repo.sh").write_text(
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
    (case_dir / "setup_env.sh").write_text("echo ok\n", encoding="utf-8")
    (case_dir / "run_verification.py").write_text('REPO_PATH = "/testbed/eslint"\n', encoding="utf-8")

    runtime = prepare_local_runtime_scripts(case_dir)

    rewritten = (runtime.runtime_dir / "setup_repo.sh").read_text(encoding="utf-8")
    assert "codex_clone_or_restore_repo" in rewritten
    assert "https://codeload.github.com/${owner}/${repo}/tar.gz/${commit}" in rewritten
    assert "4e5e9befb95bc1fc7fbcb145825b8e0451e5bc6c" in rewritten
    assert "if [ ! -f .codex-archive-snapshot ]; then" in rewritten


def test_prepare_local_runtime_scripts_makes_run_verification_py39_compatible(tmp_path: Path):
    case_dir = tmp_path / "case"
    case_dir.mkdir()
    (case_dir / "setup_repo.sh").write_text("echo ok\n", encoding="utf-8")
    (case_dir / "setup_env.sh").write_text("echo ok\n", encoding="utf-8")
    (case_dir / "run_verification.py").write_text(
        "def parse_report() -> dict | None:\n    return {}\n",
        encoding="utf-8",
    )

    runtime = prepare_local_runtime_scripts(case_dir)

    rewritten = (runtime.runtime_dir / "run_verification.py").read_text(encoding="utf-8")
    assert rewritten.startswith("from __future__ import annotations\n")
