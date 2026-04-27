from pathlib import Path
import re
from typing import Dict, Optional


_GITHUB_CLONE_RE = re.compile(
    r"git clone https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/.]+)\.git (?P<target>\S+)"
)


def parse_github_clone(line: str) -> Optional[Dict[str, str]]:
    match = _GITHUB_CLONE_RE.search(line.strip())
    if not match:
        return None
    return match.groupdict()


def build_cached_clone_replacement(
    *,
    owner: str,
    repo: str,
    target: str,
    repo_cache_root: Path,
) -> str:
    cache_path = repo_cache_root / f"{owner}__{repo}"
    return f"git clone {cache_path} {target}"
