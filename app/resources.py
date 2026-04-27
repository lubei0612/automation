from dataclasses import dataclass
import os

from app.config import RunMode


@dataclass(frozen=True)
class MachineProfile:
    cpu_count: int
    total_memory_gb: int
    free_memory_gb: int


def recommend_case_concurrency(profile: MachineProfile, run_mode: RunMode) -> int:
    if run_mode is RunMode.INTERACTIVE:
        return 1 if profile.free_memory_gb < 16 else 2
    return max(1, min(profile.cpu_count // 2, profile.free_memory_gb // 8))


def detect_machine_profile() -> MachineProfile:
    cpu_count = os.cpu_count() or 1
    total_memory_gb = 16
    free_memory_gb = 8
    try:
        import shutil
        import subprocess

        total_bytes = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip())
        total_memory_gb = max(1, total_bytes // (1024 ** 3))
        vm_stat_output = subprocess.check_output(["vm_stat"], text=True)
        page_size = 4096
        free_pages = 0
        speculative_pages = 0
        for line in vm_stat_output.splitlines():
            if "page size of" in line:
                page_size = int(line.split("page size of", 1)[1].split("bytes", 1)[0].strip())
            if line.startswith("Pages free:"):
                free_pages = int(line.split(":", 1)[1].strip().rstrip("."))
            if line.startswith("Pages speculative:"):
                speculative_pages = int(line.split(":", 1)[1].strip().rstrip("."))
        free_memory_gb = max(1, ((free_pages + speculative_pages) * page_size) // (1024 ** 3))
    except Exception:
        pass

    return MachineProfile(
        cpu_count=cpu_count,
        total_memory_gb=total_memory_gb,
        free_memory_gb=free_memory_gb,
    )
