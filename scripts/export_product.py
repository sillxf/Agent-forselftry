"""Standalone developer source export; no history, runtime data or secrets."""

import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

FOLDERS = (
    "app",
    "frontend",
    "mcp_server",
    "migrations",
    "tests",
    "evaluation",
    "scripts",
    "docker",
    "docs",
    ".github",
)
FILES = (
    "README.md",
    "启动.cmd",
    "停止.cmd",
    "AGENTS.md",
    "pyproject.toml",
    "requirements.txt",
    ".env.example",
    ".gitignore",
    ".gitattributes",
    ".dockerignore",
    "docker-compose.yml",
)
EXCLUDE = {"node_modules", "__pycache__", ".pytest_cache", ".ruff_cache", "results"}


def export(destination):
    root = Path(__file__).resolve().parents[1]
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("Use a new archive path")
    paths = [root / name for name in FILES] + [root / "storage/.gitignore"]
    for directory in FOLDERS:
        paths.extend(
            p
            for p in (root / directory).rglob("*")
            if p.is_file()
            and not EXCLUDE.intersection(p.parts)
            and not p.name.startswith(".env")
            and p.suffix not in {".pyc", ".pyo"}
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "x", ZIP_DEFLATED) as archive:
        for path in sorted(set(paths)):
            archive.write(path, path.relative_to(root))
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("destination")
    print(export(parser.parse_args().destination))
