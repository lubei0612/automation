from typing import List, Sequence, Tuple


def build_docker_build_command(*, context_dir: str, image_tag: str) -> List[str]:
    return ["docker", "build", context_dir, "-t", image_tag]


def build_docker_run_command(*, image_tag: str, mounts: Sequence[Tuple[str, str]]) -> List[str]:
    command: List[str] = ["docker", "run", "--rm", "-i"]
    for source, target in mounts:
        command.extend(["-v", f"{source}:{target}"])
    command.append(image_tag)
    return command
