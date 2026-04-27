import os
from pathlib import Path
from typing import Callable

from app.batch_runner import run_initialized_batch
from app.case_processor import CaseProcessingContext, process_case
from app.config import BatchConfig, RunMode
from app.orchestrator import initialize_batch_workspace
from app.proxy import enable_clash_proxy_if_available
from app.resources import detect_machine_profile
from app.scheduler import choose_case_concurrency


def build_default_config(root: Path) -> BatchConfig:
    run_mode = RunMode(os.environ.get("AUTOMATION_RUN_MODE", RunMode.INTERACTIVE.value))
    max_case_concurrency = os.environ.get("AUTOMATION_MAX_CASE_CONCURRENCY")
    return BatchConfig(
        input_dir=root / "input_zips",
        output_root=root / "batches",
        repo_cache_root=root / "repo_cache",
        run_mode=run_mode,
        max_case_concurrency=None if not max_case_concurrency else int(max_case_concurrency),
        model_name=os.environ.get("AUTOMATION_MODEL_NAME"),
    )


def run_once(
    config: BatchConfig,
    *,
    initialize_workspace: Callable = initialize_batch_workspace,
    batch_runner: Callable = run_initialized_batch,
    processor: Callable = None,
    detect_machine_profile_fn: Callable = detect_machine_profile,
) -> str:
    if processor is None:
        def default_processor(batch_case):
            context = CaseProcessingContext(
                case_id=batch_case.case_id,
                source_zip=batch_case.source_zip,
                extracted_dir=batch_case.extracted_dir,
                paths=workspace.paths,
            )
            result = process_case(context)
            return {"classification": result.classification}

        processor = default_processor
    profile = detect_machine_profile_fn()
    max_workers = choose_case_concurrency(config, profile)
    workspace = initialize_workspace(config, "2026-04-24", 1)
    batch_runner(workspace=workspace, processor=processor, max_workers=max_workers)
    return workspace.batch_id


def main(*, root: Path = None, run_once_fn: Callable = run_once) -> str:
    enable_clash_proxy_if_available()
    effective_root = Path.cwd() if root is None else root
    config = build_default_config(effective_root)
    return run_once_fn(config)


if __name__ == "__main__":
    batch_id = main()
    print(batch_id)
