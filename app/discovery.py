from pathlib import Path
from typing import List


def discover_zip_inputs(input_dir: Path) -> List[Path]:
    return sorted(
        path
        for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".zip"
    )
