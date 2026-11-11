"""Legacy embedded entry point; prefer the independent service for new integrations."""
from rag_service.core.retriever import *
from rag_service.core.retriever import KnowledgeRetriever as CoreRetriever
from app.config import RAG_KNOWLEDGE_DIR, RAG_STORAGE_DIR

class KnowledgeRetriever(CoreRetriever):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("knowledge_dir", RAG_KNOWLEDGE_DIR)
        kwargs.setdefault("storage_dir", RAG_STORAGE_DIR)
        super().__init__(*args, **kwargs)
