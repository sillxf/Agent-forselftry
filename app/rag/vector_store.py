"""Compatibility import for the original RAG module path."""
from app.rag.indexing.vector_store import FaissVectorStore

VectorStore = FaissVectorStore
