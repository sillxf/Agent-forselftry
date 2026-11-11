"""Compatibility alias; canonical implementation lives in rag_service.core.indexing.build_service."""
import importlib
import sys
sys.modules[__name__] = importlib.import_module("rag_service.core.indexing.build_service")
