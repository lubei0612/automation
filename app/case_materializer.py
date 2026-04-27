from pathlib import Path

from app.paths import BatchPaths


def select_output_directory(paths: BatchPaths, classification: str) -> Path:
    return {
        "accepted": paths.accepted_dir,
        "unresolved": paths.unresolved_dir,
        "invalid": paths.invalid_dir,
        "timeout": paths.timeout_dir,
    }[classification]
