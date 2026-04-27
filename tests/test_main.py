from pathlib import Path

import os

from app.main import build_default_config, main, run_once


def test_build_default_config_points_to_portable_directories(tmp_path: Path):
    config = build_default_config(tmp_path)

    assert config.input_dir == tmp_path / "input_zips"
    assert config.output_root == tmp_path / "batches"


def test_run_once_initializes_batch_and_returns_batch_id(tmp_path: Path):
    input_dir = tmp_path / "input_zips"
    output_root = tmp_path / "batches"
    input_dir.mkdir()
    output_root.mkdir()

    config = build_default_config(tmp_path)

    def fake_initialize(config_arg, date_str, sequence):
        class FakeWorkspace:
            batch_id = "2026-04-24-batch-001"
            paths = None
            cases = []

        return FakeWorkspace()

    def fake_run_initialized_batch(*, workspace, processor, max_workers):
        return {"accepted": 0}

    batch_id = run_once(
        config,
        initialize_workspace=fake_initialize,
        batch_runner=fake_run_initialized_batch,
        processor=lambda case: {"classification": "accepted"},
    )

    assert batch_id == "2026-04-24-batch-001"


def test_main_uses_current_directory_by_default(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    seen = {}

    def fake_run_once(config, **kwargs):
        seen["config"] = config
        return "2026-04-24-batch-001"

    batch_id = main(run_once_fn=fake_run_once)

    assert batch_id == "2026-04-24-batch-001"
    assert seen["config"].input_dir == tmp_path / "input_zips"


def test_build_default_config_uses_interactive_mode_by_default(tmp_path: Path):
    config = build_default_config(tmp_path)

    assert config.run_mode.value == "interactive"


def test_build_default_config_can_read_runtime_overrides_from_env(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AUTOMATION_RUN_MODE", "dedicated")
    monkeypatch.setenv("AUTOMATION_MAX_CASE_CONCURRENCY", "4")
    monkeypatch.setenv("AUTOMATION_MODEL_NAME", "gpt-5.5")

    config = build_default_config(tmp_path)

    assert config.run_mode.value == "dedicated"
    assert config.max_case_concurrency == 4
    assert config.model_name == "gpt-5.5"


def test_run_once_can_use_default_processor(tmp_path: Path):
    input_dir = tmp_path / "input_zips"
    output_root = tmp_path / "batches"
    input_dir.mkdir()
    output_root.mkdir()

    config = build_default_config(tmp_path)

    def fake_initialize(config_arg, date_str, sequence):
        class FakePaths:
            reports_dir = tmp_path

        class FakeWorkspace:
            batch_id = "2026-04-24-batch-001"
            paths = FakePaths()
            cases = []

        return FakeWorkspace()

    def fake_run_initialized_batch(*, workspace, processor, max_workers):
        assert callable(processor)
        return {"accepted": 0}

    batch_id = run_once(
        config,
        initialize_workspace=fake_initialize,
        batch_runner=fake_run_initialized_batch,
    )

    assert batch_id == "2026-04-24-batch-001"


def test_run_once_passes_recommended_concurrency_to_batch_runner(tmp_path: Path):
    input_dir = tmp_path / "input_zips"
    output_root = tmp_path / "batches"
    input_dir.mkdir()
    output_root.mkdir()

    config = build_default_config(tmp_path)

    seen = {}

    def fake_initialize(config_arg, date_str, sequence):
        class FakePaths:
            reports_dir = tmp_path

        class FakeWorkspace:
            batch_id = "2026-04-24-batch-001"
            paths = FakePaths()
            cases = []

        return FakeWorkspace()

    def fake_batch_runner(*, workspace, processor, max_workers):
        seen["max_workers"] = max_workers
        return {"accepted": 0}

    def fake_machine_profile():
        from app.resources import MachineProfile
        return MachineProfile(cpu_count=8, total_memory_gb=32, free_memory_gb=20)

    batch_id = run_once(
        config,
        initialize_workspace=fake_initialize,
        batch_runner=fake_batch_runner,
        detect_machine_profile_fn=fake_machine_profile,
    )

    assert batch_id == "2026-04-24-batch-001"
    assert seen["max_workers"] >= 1
