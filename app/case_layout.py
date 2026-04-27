from pathlib import Path


def resolve_case_root(extracted_dir: Path) -> Path:
    top_level_files = [path for path in extracted_dir.iterdir() if path.is_file()]
    if top_level_files:
        return extracted_dir

    top_level_dirs = [path for path in extracted_dir.iterdir() if path.is_dir()]
    if len(top_level_dirs) == 1:
        return top_level_dirs[0]
    return extracted_dir
