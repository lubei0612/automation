from pathlib import Path

from app.baseline_verifier import verify_baseline
from app.executor import CommandExecutionResult


def test_verify_baseline_executes_planned_steps_with_injected_executor(tmp_path: Path):
    calls = []

    def fake_executor(command, *, cwd, timeout_seconds):
        calls.append((command, cwd, timeout_seconds))
        return CommandExecutionResult(
            command=command,
            exit_code=0,
            stdout="ok",
            stderr="",
            timed_out=False,
        )

    result = verify_baseline(
        workspace=tmp_path,
        test_targets=["tests/test_a.py"],
        code_patch_path=str(tmp_path / "code.patch"),
        test_patch_path=str(tmp_path / "test.patch"),
        executor=fake_executor,
    )

    assert result.valid is True
    assert len(calls) == 5
    assert calls[0][0][0:2] == ["python3", "-m"]


def test_verify_baseline_returns_invalid_on_failed_step(tmp_path: Path):
    call_index = {"value": 0}

    def fake_executor(command, *, cwd, timeout_seconds):
        call_index["value"] += 1
        exit_code = 1 if call_index["value"] == 3 else 0
        return CommandExecutionResult(
            command=command,
            exit_code=exit_code,
            stdout="",
            stderr="boom" if exit_code else "",
            timed_out=False,
        )

    result = verify_baseline(
        workspace=tmp_path,
        test_targets=["tests/test_a.py"],
        code_patch_path=str(tmp_path / "code.patch"),
        test_patch_path=str(tmp_path / "test.patch"),
        executor=fake_executor,
    )

    assert result.valid is False
    assert result.failed_step == "run_fail_to_pass_tests"
