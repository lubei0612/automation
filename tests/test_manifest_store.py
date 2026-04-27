import json
from pathlib import Path

from app.manifest_store import write_case_manifest
from app.state_machine import CaseState


def test_write_case_manifest_persists_state_and_classification(tmp_path: Path):
    manifest_path = tmp_path / "case-0001.json"

    write_case_manifest(
        manifest_path,
        {
            "case_id": "case-0001",
            "state": CaseState.INVALID.value,
            "classification": "invalid",
        },
    )

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["case_id"] == "case-0001"
    assert data["classification"] == "invalid"
