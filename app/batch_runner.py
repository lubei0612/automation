from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Callable, Iterable

from app.metrics import BatchMetrics
from app.reports import build_batch_summary


@dataclass(frozen=True)
class BatchCase:
    case_id: str
    source_zip: Path
    extracted_dir: Path


def run_initialized_batch(*, workspace, processor: Callable[[BatchCase], dict], max_workers: int = 1) -> BatchMetrics:
    cases = [
        BatchCase(
            case_id=f"case-{index:04d}",
            source_zip=case.source_zip,
            extracted_dir=case.extracted_dir,
        )
        for index, case in enumerate(workspace.cases, start=1)
    ]
    return run_batch(cases=cases, paths=workspace.paths, processor=processor, max_workers=max_workers)


def run_batch(
    *,
    cases: Iterable[BatchCase],
    paths,
    processor: Callable[[BatchCase], dict],
    max_workers: int = 1,
) -> BatchMetrics:
    metrics = BatchMetrics()
    failures = [("case_id", "classification")]
    delivery_items = []
    failure_items = []
    case_list = list(cases)

    if max_workers > 1:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(processor, case_list))
    else:
        results = [processor(case) for case in case_list]

    for case, result in zip(case_list, results):
        classification = result["classification"]
        if classification == "accepted":
            metrics.accepted += 1
        elif classification == "unresolved":
            metrics.unresolved += 1
        elif classification == "invalid":
            metrics.invalid += 1
        elif classification == "timeout":
            metrics.timeout += 1
        if classification == "accepted":
            delivery_items.append(
                {
                    "case_id": case.case_id,
                    "source_zip_name": case.source_zip.name,
                    "source_zip_path": str(case.source_zip),
                    "delivery_path": str(paths.delivery_dir / case.case_id),
                }
            )
        else:
            failures.append((case.case_id, classification))
            failure_items.append(
                {
                    "case_id": case.case_id,
                    "classification": classification,
                    "source_zip_name": case.source_zip.name,
                    "source_zip_path": str(case.source_zip),
                    "case_output_path": str(getattr(paths, f"{classification}_dir") / case.case_id),
                }
            )

    summary = build_batch_summary(
        metrics,
        run_metadata={
            "case_concurrency": max_workers,
            "delivery_dir": str(paths.delivery_dir),
        },
    )
    (paths.reports_dir / "batch_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (paths.reports_dir / "delivery_manifest.json").write_text(
        json.dumps(
            {
                "accepted_count": metrics.accepted,
                "delivery_dir": str(paths.delivery_dir),
                "items": delivery_items,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (paths.reports_dir / "failure_manifest.json").write_text(
        json.dumps(
            {
                "failed_count": len(failure_items),
                "items": failure_items,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (paths.reports_dir / "failures.csv").write_text(
        "\n".join(f"{case_id},{classification}" for case_id, classification in failures) + "\n",
        encoding="utf-8",
    )
    (paths.reports_dir / "batch_summary.md").write_text(
        "\n".join(
            [
                "# Batch Summary",
                "",
                f"Accepted: {metrics.accepted}",
                f"Unresolved: {metrics.unresolved}",
                f"Invalid: {metrics.invalid}",
                f"Timeout: {metrics.timeout}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return metrics
