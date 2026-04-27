from pathlib import Path

from app.agent_adapter import AgentRunRequest


def test_agent_run_request_tracks_prompt_and_workspace(tmp_path: Path):
    request = AgentRunRequest(prompt="fix bug", workspace=tmp_path, model_name=None)

    assert request.prompt == "fix bug"
    assert request.workspace == tmp_path
