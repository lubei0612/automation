import json
from pathlib import Path
from typing import Dict


def load_case_metadata(case_dir: Path) -> Dict:
    json_files = sorted(path for path in case_dir.iterdir() if path.is_file() and path.suffix.lower() == ".json")
    if not json_files:
        return {}
    return json.loads(json_files[0].read_text(encoding="utf-8"))
