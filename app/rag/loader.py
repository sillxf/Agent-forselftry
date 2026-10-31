"""Compatibility loader and deterministic discovery for the new ingestion path."""
from pathlib import Path

from app.config import RAG_KNOWLEDGE_DIR
from app.rag.ingestion.docling_parser import DoclingParser, SUPPORTED_EXTENSIONS


def discover_documents(directory=RAG_KNOWLEDGE_DIR) -> list[Path]:
    path = Path(directory)
    if not path.exists():
        return []
    if not path.is_dir():
        raise ValueError(f"Knowledge directory is not a directory: {path}")
    return sorted((file for file in path.rglob("*")
                   if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS),
                  key=lambda file: file.relative_to(path).as_posix())


def load_documents(directory=RAG_KNOWLEDGE_DIR):
    """Keep filename/content keys for callers using the original loader."""
    parser = DoclingParser()
    return [{"filename": parsed.document.filename, "content": parsed.markdown}
            for parsed in (parser.parse(file) for file in discover_documents(directory))]
