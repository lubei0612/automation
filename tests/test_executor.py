from pathlib import Path

from app.executor import CommandExecutionResult, run_command


def test_run_command_captures_stdout_and_exit_code(tmp_path: Path):
    result = run_command(
        ["python3", "-c", "print('ok')"],
        cwd=tmp_path,
        timeout_seconds=5,
    )

    assert result.exit_code == 0
    assert result.timed_out is False
    assert result.stdout.strip() == "ok"


def test_run_command_marks_timeout(tmp_path: Path):
    result = run_command(
        ["python3", "-c", "import time; time.sleep(1.0)"],
        cwd=tmp_path,
        timeout_seconds=0.01,
    )

    assert result.timed_out is True
    assert result.exit_code != 0
