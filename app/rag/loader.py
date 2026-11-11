"""Legacy directory defaults, delegated to the standalone ingestion helpers."""

from app.config import RAG_KNOWLEDGE_DIR
from rag_service.core.loader import (
    discover_documents as _discover,
    load_documents as _load,
)
from rag_service.core.ingestion.docling_parser import (
    DoclingParser,
    SUPPORTED_EXTENSIONS,
)


def discover_documents(directory=RAG_KNOWLEDGE_DIR):
    return _discover(directory)


def load_documents(directory=RAG_KNOWLEDGE_DIR):
    return _load(directory)
