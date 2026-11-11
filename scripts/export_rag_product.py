"""Export only the standalone product sources; no Agent, credentials or runtime data."""

import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def export(destination):
    root = Path(__file__).resolve().parents[1]
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("Use a new archive path")
    paths = [root / "pyproject.toml", root / "RAG_PRODUCT.md", root / ".dockerignore"]
    for folder in ["rag_service", "frontend", "deploy"]:
        paths.extend(
            p
            for p in (root / folder).rglob("*")
            if p.is_file() and not {"__pycache__", "node_modules"}.intersection(p.parts)
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "x", ZIP_DEFLATED) as archive:
        archive.writestr(
            ".gitignore",
            (root / "deploy/product.gitignore").read_text(encoding="utf-8"),
        )
        for path in paths:
            archive.write(path, path.relative_to(root))
    return destination


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("destination")
    print(export(p.parse_args().destination))
