from typing import List, Optional


def build_codex_command(*, prompt: str, workdir: str, model_name: Optional[str]) -> List[str]:
    command = ["codex", "exec", "--skip-git-repo-check", prompt]
    if model_name:
        command.extend(["-m", model_name])
    return command
