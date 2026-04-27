from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BatchPaths:
    batch_root: Path
    delivery_dir: Path
    accepted_dir: Path
    unresolved_dir: Path
    invalid_dir: Path
    timeout_dir: Path
    reports_dir: Path
    workspace_dir: Path
    manifests_dir: Path


def build_batch_paths(batch_root: Path) -> BatchPaths:
    return BatchPaths(
        batch_root=batch_root,
        delivery_dir=batch_root / "delivery",
        accepted_dir=batch_root / "accepted",
        unresolved_dir=batch_root / "unresolved",
        invalid_dir=batch_root / "invalid",
        timeout_dir=batch_root / "timeout",
        reports_dir=batch_root / "reports",
        workspace_dir=batch_root / "workspace",
        manifests_dir=batch_root / "manifests",
    )
