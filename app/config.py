import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


LLM_MODEL = os.getenv(
    "LLM_MODEL"
)

LLM_API_KEY = os.getenv(
    "LLM_API_KEY"
)

LLM_BASE_URL = os.getenv(
    "LLM_BASE_URL"
)

# Relative RAG paths are resolved against the repository, not the process cwd.

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _rag_path(name: str, default: str) -> Path:
    path = Path(os.getenv(name, default)).expanduser()
    return path if path.is_absolute() else _PROJECT_ROOT / path


RAG_KNOWLEDGE_DIR = _rag_path("RAG_KNOWLEDGE_DIR", "app/knowledge")
RAG_STORAGE_DIR = _rag_path("RAG_STORAGE_DIR", "app/storage")
# Preserve the lightweight baseline; evaluate BAAI/bge-m3 via configuration.
RAG_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
RAG_PARENT_MAX_TOKENS = int(os.getenv("RAG_PARENT_MAX_TOKENS", "1600"))
RAG_CHILD_MAX_TOKENS = int(os.getenv("RAG_CHILD_MAX_TOKENS", "400"))
RAG_CHILD_OVERLAP_TOKENS = int(os.getenv("RAG_CHILD_OVERLAP_TOKENS", "60"))
RAG_DENSE_TOP_K = int(os.getenv("RAG_DENSE_TOP_K", "20"))
RAG_BM25_TOP_K = int(os.getenv("RAG_BM25_TOP_K", "20"))
RAG_OCR_ENABLED = os.getenv("RAG_OCR_ENABLED", "true").lower() in {"1", "true", "yes"}
