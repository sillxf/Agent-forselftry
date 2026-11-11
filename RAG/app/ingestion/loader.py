"""Deterministic discovery within an explicitly selected knowledge directory."""

from pathlib import Path

from app.ingestion.docling_parser import (
    SUPPORTED_EXTENSIONS,
)


def discover_documents(directory) -> list[Path]:
    path = Path(directory)
    if not path.exists():
        return []
    if not path.is_dir():
        raise ValueError(f"Knowledge directory is not a directory: {path}")
    return sorted(
        (
            file
            for file in path.rglob("*")
            if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS
        ),
        key=lambda file: file.relative_to(path).as_posix(),
    )
