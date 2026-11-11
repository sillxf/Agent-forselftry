"""Compatibility import for the original RAG module path."""

from rag_service.core.indexing.vector_store import FaissVectorStore

VectorStore = FaissVectorStore
