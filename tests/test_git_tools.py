from pathlib import Path

from app.executor import CommandExecutionResult
from app.git_tools import capture_final_diff


def test_capture_final_diff_runs_git_diff(tmp_path: Path):
    seen = {}

    def fake_executor(command, *, cwd, timeout_seconds):
        seen["command"] = command
        seen["cwd"] = cwd
        return CommandExecutionResult(
            command=command,
            exit_code=0,
            stdout="diff --git a/a b/a\n",
            stderr="",
            timed_out=False,
        )

    diff = capture_final_diff(tmp_path, executor=fake_executor)

    assert diff == "diff --git a/a b/a\n"
    assert seen["command"] == ["git", "diff"]
    assert seen["cwd"] == tmp_path
