from app.config import RunMode
from app.resources import MachineProfile, recommend_case_concurrency


def test_recommend_case_concurrency_is_conservative_for_interactive_mode():
    profile = MachineProfile(cpu_count=8, total_memory_gb=32, free_memory_gb=20)

    assert recommend_case_concurrency(profile, RunMode.INTERACTIVE) <= 2


def test_recommend_case_concurrency_scales_up_for_dedicated_mode():
    profile = MachineProfile(cpu_count=16, total_memory_gb=64, free_memory_gb=48)

    assert recommend_case_concurrency(profile, RunMode.DEDICATED) >= 2
