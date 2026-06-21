import os
from pathlib import Path

from cognee.modules.ingestion.exceptions import IngestionError


def get_allowed_local_path_roots() -> list[Path]:
    roots: list[Path] = [Path.cwd().resolve()]

    data_root = os.getenv("DATA_ROOT_DIRECTORY")
    if data_root:
        roots.append(Path(data_root).expanduser().resolve())

    extra_roots = os.getenv("ALLOWED_LOCAL_FILE_PATH_PREFIXES", "")
    for prefix in extra_roots.split(","):
        prefix = prefix.strip()
        if prefix:
            roots.append(Path(prefix).expanduser().resolve())

    unique_roots: list[Path] = []
    for root in roots:
        if root not in unique_roots:
            unique_roots.append(root)
    return unique_roots


def validate_local_file_path(path: Path) -> Path:
    resolved = path.expanduser().resolve()

    for root in get_allowed_local_path_roots():
        try:
            resolved.relative_to(root)
            return resolved
        except ValueError:
            continue

    raise IngestionError(
        message=(
            "Local file path is outside allowed directories. "
            "Configure ALLOWED_LOCAL_FILE_PATH_PREFIXES or use a path under the working directory."
        )
    )


def local_path_to_file_uri(path: Path) -> str:
    validated = validate_local_file_path(path)
    return validated.as_uri()
