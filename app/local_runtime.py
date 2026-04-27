from dataclasses import dataclass
from pathlib import Path
import re
from typing import Optional

from app.repo_cache import build_cached_clone_replacement, parse_github_clone


@dataclass(frozen=True)
class LocalRuntimeScripts:
    runtime_dir: Path
    testbed_root: Path
    setup_repo_script: Path
    setup_env_script: Path
    run_verification_script: Path


def _rewrite_testbed_paths(text: str, testbed_root: Path) -> str:
    return text.replace("/testbed", str(testbed_root))


def _make_python39_compatible(text: str) -> str:
    future_import = "from __future__ import annotations\n"
    if text.startswith(future_import):
        return text
    return future_import + text


_GIT_CHECKOUT_RE = re.compile(r"^git checkout (?P<commit>[0-9a-f]{7,40})\s*$")


def _find_checkout_commit(text: str) -> Optional[str]:
    for line in text.splitlines():
        match = _GIT_CHECKOUT_RE.match(line.strip())
        if match:
            return match.group("commit")
    return None


def _inject_archive_fallback(text: str) -> str:
    lines = text.splitlines()
    clone_index = None
    clone_info = None
    for index, line in enumerate(lines):
        parsed = parse_github_clone(line)
        if parsed:
            clone_index = index
            clone_info = parsed
            break

    if clone_info is None or clone_index is None:
        return text

    commit = _find_checkout_commit(text)
    if commit is None:
        return text

    helper = "\n".join(
        [
            "codex_clone_or_restore_repo() {",
            '  local owner="$1"',
            '  local repo="$2"',
            '  local target="$3"',
            '  local commit="$4"',
            '  local source_url="https://github.com/${owner}/${repo}.git"',
            '  local archive_url="https://codeload.github.com/${owner}/${repo}/tar.gz/${commit}"',
            '  local allow_archive="${ENABLE_GITHUB_ARCHIVE_FALLBACK:-1}"',
            "",
            '  if git clone "$source_url" "$target"; then',
            "    return 0",
            "  fi",
            "",
            '  if [ "$allow_archive" = "0" ]; then',
            "    return 1",
            "  fi",
            "",
            '  echo "[fallback] downloading archive for ${owner}/${repo}@${commit}"',
            '  rm -rf "$target"',
            '  mkdir -p "$target"',
            '  local tmpdir',
            '  tmpdir="$(mktemp -d)"',
            '  local archive_path="${tmpdir}/repo.tar.gz"',
            '  curl -fsSL "$archive_url" -o "$archive_path"',
            '  tar -xzf "$archive_path" -C "$target" --strip-components=1',
            '  touch "$target/.codex-archive-snapshot"',
            '  rm -rf "$tmpdir"',
            "}",
            "",
        ]
    )

    lines[clone_index] = (
        f'codex_clone_or_restore_repo "{clone_info["owner"]}" "{clone_info["repo"]}" '
        f'"{clone_info["target"]}" "{commit}"'
    )

    for index, line in enumerate(lines):
        if _GIT_CHECKOUT_RE.match(line.strip()):
            lines[index] = (
                f'if [ ! -f .codex-archive-snapshot ]; then\n'
                f'  git checkout {commit}\n'
                f'else\n'
                f'  echo "[fallback] archive snapshot already pinned to {commit}"\n'
                f'fi'
            )
            break

    return helper + "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def _rewrite_clone_to_cache(text: str, repo_cache_root: Path) -> str:
    replaced = False
    lines = []
    for line in text.splitlines():
        parsed = parse_github_clone(line)
        if parsed:
            cache_path = repo_cache_root / f"{parsed['owner']}__{parsed['repo']}"
            if cache_path.exists():
                replaced = True
                line = build_cached_clone_replacement(
                    owner=parsed["owner"],
                    repo=parsed["repo"],
                    target=parsed["target"],
                    repo_cache_root=repo_cache_root,
                )
        lines.append(line)
    rewritten = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    if replaced:
        return rewritten
    return _inject_archive_fallback(rewritten)


def prepare_local_runtime_scripts(case_dir: Path, *, repo_cache_root: Path = None) -> LocalRuntimeScripts:
    runtime_dir = case_dir / ".runtime"
    testbed_root = runtime_dir / "testbed"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    testbed_root.mkdir(parents=True, exist_ok=True)

    setup_repo_src = case_dir / "setup_repo.sh"
    setup_env_src = case_dir / "setup_env.sh"
    run_verification_src = case_dir / "run_verification.py"

    setup_repo_dst = runtime_dir / "setup_repo.sh"
    setup_env_dst = runtime_dir / "setup_env.sh"
    run_verification_dst = runtime_dir / "run_verification.py"

    setup_repo_text = _rewrite_testbed_paths(
        setup_repo_src.read_text(encoding="utf-8", errors="replace"),
        testbed_root,
    )
    if repo_cache_root is not None:
        setup_repo_text = _rewrite_clone_to_cache(setup_repo_text, repo_cache_root)
    else:
        setup_repo_text = _inject_archive_fallback(setup_repo_text)
    setup_repo_dst.write_text(setup_repo_text, encoding="utf-8")
    setup_env_dst.write_text(
        _rewrite_testbed_paths(setup_env_src.read_text(encoding="utf-8", errors="replace"), testbed_root),
        encoding="utf-8",
    )
    run_verification_dst.write_text(
        _make_python39_compatible(
            _rewrite_testbed_paths(
                run_verification_src.read_text(encoding="utf-8", errors="replace"),
                testbed_root,
            )
        ),
        encoding="utf-8",
    )

    return LocalRuntimeScripts(
        runtime_dir=runtime_dir,
        testbed_root=testbed_root,
        setup_repo_script=setup_repo_dst,
        setup_env_script=setup_env_dst,
        run_verification_script=run_verification_dst,
    )
