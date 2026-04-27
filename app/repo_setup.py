from pathlib import Path


def extract_repo_path_from_setup_repo(script_path: Path) -> str:
    for raw_line in script_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line.startswith("git clone"):
            continue
        parts = line.split()
        if parts:
            return parts[-1]
    return ""
