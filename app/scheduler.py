from app.config import BatchConfig
from app.resources import MachineProfile, recommend_case_concurrency


def choose_case_concurrency(config: BatchConfig, profile: MachineProfile) -> int:
    if config.max_case_concurrency is not None:
        return config.max_case_concurrency
    return recommend_case_concurrency(profile, config.run_mode)
