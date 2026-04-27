from app.codex_runner import build_codex_command


def test_build_codex_command_includes_prompt_without_cwd_flag():
    command = build_codex_command(
        prompt="Fix the issue",
        workdir="C:/work/case",
        model_name="gpt-5-codex",
    )

    assert command[0:2] == ["codex", "exec"]
    assert "Fix the issue" in command
    assert "--cwd" not in command
    assert "C:/work/case" not in command
    assert "--skip-git-repo-check" in command
