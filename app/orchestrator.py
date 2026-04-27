from dataclasses import dataclass
from pathlib import Path
from typing import List

from app.case_layout import resolve_case_root
from app.config import BatchConfig
from app.discovery import discover_zip_inputs
from app.extraction import extract_zip_to_directory
from app.paths import BatchPaths, build_batch_paths


@dataclass(frozen=True)
class CaseWorkspace:
    source_zip: Path
    extracted_dir: Path


@dataclass(frozen=True)
class BatchWorkspace:
    batch_id: str
    paths: BatchPaths
    cases: List[CaseWorkspace]


def build_batch_id(date_str: str, sequence: int) -> str:
    return f"{date_str}-batch-{sequence:03d}"


def initialize_batch_workspace(
    config: BatchConfig,
    date_str: str,
    sequence: int,
) -> BatchWorkspace:
    batch_id = build_batch_id(date_str, sequence)
    paths = build_batch_paths(config.output_root / batch_id)
    for directory in (
        paths.batch_root,
        paths.delivery_dir,
        paths.accepted_dir,
        paths.unresolved_dir,
        paths.invalid_dir,
        paths.timeout_dir,
        paths.reports_dir,
        paths.workspace_dir,
        paths.manifests_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    cases: List[CaseWorkspace] = []
    for index, archive in enumerate(discover_zip_inputs(config.input_dir), start=1):
        extracted_dir = paths.workspace_dir / f"case-{index:04d}" / "extracted"
        extract_zip_to_directory(archive, extracted_dir)
        cases.append(CaseWorkspace(source_zip=archive, extracted_dir=resolve_case_root(extracted_dir)))

    return BatchWorkspace(batch_id=batch_id, paths=paths, cases=cases)
