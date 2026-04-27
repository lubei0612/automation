from pathlib import Path

from app.preflight import extract_test_targets


def test_extract_test_targets_returns_changed_test_files(tmp_path: Path):
    patch = tmp_path / "test.patch"
    patch.write_text(
        "diff --git a/tests/test_a.py b/tests/test_a.py\n"
        "--- a/tests/test_a.py\n"
        "+++ b/tests/test_a.py\n",
        encoding="utf-8",
    )

    assert extract_test_targets(patch) == ["tests/test_a.py"]
