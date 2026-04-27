from pathlib import Path

from app.codex_runtime import run_codex_task
from app.executor import CommandExecutionResult


def test_run_codex_task_uses_built_command_and_returns_result(tmp_path: Path):
    captured = {}

    def fake_executor(command, *, cwd, timeout_seconds):
        captured["command"] = command
        captured["cwd"] = cwd
        return CommandExecutionResult(
            command=command,
            exit_code=0,
            stdout="done",
            stderr="",
            timed_out=False,
        )

    result = run_codex_task(
        prompt="Fix the bug",
        workspace=tmp_path,
        model_name="gpt-5-codex",
        executor=fake_executor,
    )

    assert result.exit_code == 0
    assert captured["command"][0:2] == ["codex", "exec"]
    assert captured["cwd"] == tmp_path
