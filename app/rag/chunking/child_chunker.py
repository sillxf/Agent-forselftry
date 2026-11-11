"""Compatibility alias; canonical implementation lives in rag_service.core.chunking.child_chunker."""
import importlib
import sys
sys.modules[__name__] = importlib.import_module("rag_service.core.chunking.child_chunker")
