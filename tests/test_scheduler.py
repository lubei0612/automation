from app.config import BatchConfig, RunMode
from app.resources import MachineProfile
from app.scheduler import choose_case_concurrency


def test_choose_case_concurrency_uses_explicit_override():
    config = BatchConfig(input_dir=None, output_root=None, max_case_concurrency=3)
    profile = MachineProfile(cpu_count=8, total_memory_gb=32, free_memory_gb=20)

    assert choose_case_concurrency(config, profile) == 3


def test_choose_case_concurrency_falls_back_to_profile_recommendation():
    config = BatchConfig(input_dir=None, output_root=None, run_mode=RunMode.INTERACTIVE)
    profile = MachineProfile(cpu_count=8, total_memory_gb=32, free_memory_gb=20)

    assert choose_case_concurrency(config, profile) <= 2
