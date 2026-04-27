import json
from pathlib import Path
import shutil
from typing import Any, Dict

from app.case_materializer import select_output_directory
from app.paths import BatchPaths


def materialize_case_output(
    *,
    paths: BatchPaths,
    classification: str,
    case_id: str,
    files: Dict[str, Any],
) -> Path:
    target_dir = select_output_directory(paths, classification) / case_id
    target_dir.mkdir(parents=True, exist_ok=True)

    for filename, content in files.items():
        file_path = target_dir / filename
        if isinstance(content, (dict, list)):
            file_path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            file_path.write_text(str(content), encoding="utf-8")

    if classification == "accepted":
        delivery_dir = paths.delivery_dir / case_id
        if delivery_dir.exists():
            shutil.rmtree(delivery_dir)
        shutil.copytree(target_dir, delivery_dir)
    return target_dir
