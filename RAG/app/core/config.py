"""Process-level defaults; per-KB build/query settings are versioned contracts."""

import os
from dotenv import load_dotenv

load_dotenv()
RAG_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "BAAI/bge-m3")
RAG_RERANKER_MODEL = os.getenv("RAG_RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
