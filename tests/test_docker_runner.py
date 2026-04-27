from app.docker_runner import build_docker_build_command, build_docker_run_command


def test_build_docker_build_command_uses_tag_and_context():
    command = build_docker_build_command(context_dir="C:/work/case", image_tag="case-001")

    assert command == ["docker", "build", "C:/work/case", "-t", "case-001"]


def test_build_docker_run_command_mounts_requested_files():
    command = build_docker_run_command(
        image_tag="case-001",
        mounts=[
            ("C:/work/test.patch", "/testbed/test.patch"),
            ("C:/work/run_verification.py", "/testbed/run_verification.py"),
        ],
    )

    assert command[:4] == ["docker", "run", "--rm", "-i"]
    assert "-v" in command
    assert "case-001" in command
