from pathlib import Path


def test_run_trial_script_exists():
    assert Path("scripts/run_trial.sh").exists()


def test_show_case_report_script_exists_and_targets_acceptance_report():
    script = Path("scripts/show_case_report.sh")
    assert script.exists()
    content = script.read_text(encoding="utf-8")
    assert "acceptance_report.json" in content
    assert "case-0001" in content


def test_run_case_once_script_exists_and_chains_trial_and_report():
    script = Path("scripts/run_case_once.sh")
    assert script.exists()
    content = script.read_text(encoding="utf-8")
    assert "run_trial.sh" in content
    assert "show_case_report.sh" in content
    assert "USE_CLASH_PROXY" in content


def test_worker_setup_mentions_delivery_directory():
    content = Path("docs/worker-setup.md").read_text(encoding="utf-8")
    assert "delivery/" in content
