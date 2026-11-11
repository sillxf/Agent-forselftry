import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


LLM_MODEL = os.getenv("LLM_MODEL")

LLM_API_KEY = os.getenv("LLM_API_KEY")

LLM_BASE_URL = os.getenv("LLM_BASE_URL")

# Relative RAG paths are resolved against the repository, not the process cwd.

_PROJECT_ROOT = Path.home() / ".rag-service"


def _rag_path(name: str, default: str) -> Path:
    path = Path(os.getenv(name, default)).expanduser()
    return path if path.is_absolute() else _PROJECT_ROOT / path


RAG_KNOWLEDGE_DIR = _rag_path("RAG_KNOWLEDGE_DIR", "legacy/knowledge")
RAG_STORAGE_DIR = _rag_path("RAG_STORAGE_DIR", "legacy/storage")
# Multilingual default validated by the Security RAG Benchmark; env overrides remain supported.
RAG_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "BAAI/bge-m3")
RAG_PARENT_MAX_TOKENS = int(os.getenv("RAG_PARENT_MAX_TOKENS", "1600"))
RAG_CHILD_MAX_TOKENS = int(os.getenv("RAG_CHILD_MAX_TOKENS", "400"))
RAG_CHILD_OVERLAP_TOKENS = int(os.getenv("RAG_CHILD_OVERLAP_TOKENS", "60"))
RAG_DENSE_TOP_K = int(os.getenv("RAG_DENSE_TOP_K", "20"))
RAG_BM25_TOP_K = int(os.getenv("RAG_BM25_TOP_K", "20"))
RAG_OCR_ENABLED = os.getenv("RAG_OCR_ENABLED", "true").lower() in {"1", "true", "yes"}

# Independent online policy; optional reranking is lazy and degrades to Hybrid.
RAG_RETRIEVAL_STRATEGY = os.getenv("RAG_RETRIEVAL_STRATEGY", "hybrid")
RAG_RERANKER_MODEL = os.getenv("RAG_RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
RAG_CONTEXT_CHAR_BUDGET = int(os.getenv("RAG_CONTEXT_CHAR_BUDGET", "24000"))
RAG_RERANKER_TIMEOUT_SECONDS = float(os.getenv("RAG_RERANKER_TIMEOUT_SECONDS", "2"))
RAG_EMBEDDING_CACHE_REVISION = os.getenv("RAG_EMBEDDING_CACHE_REVISION", "1")
