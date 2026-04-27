from pathlib import Path

from app.config import BatchConfig, RunMode


def test_batch_config_defaults_to_interactive_mode():
    config = BatchConfig(input_dir=Path("input_zips"), output_root=Path("batches"))
    assert config.run_mode is RunMode.INTERACTIVE
    assert config.case_timeout_minutes == 60


def test_batch_config_allows_override_values():
    config = BatchConfig(
        input_dir=Path("in"),
        output_root=Path("out"),
        run_mode=RunMode.DEDICATED,
        max_case_concurrency=3,
    )
    assert config.run_mode is RunMode.DEDICATED
    assert config.max_case_concurrency == 3
