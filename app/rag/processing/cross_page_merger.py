"""Compatibility alias; canonical implementation lives in rag_service.core.processing.cross_page_merger."""
import importlib
import sys
sys.modules[__name__] = importlib.import_module("rag_service.core.processing.cross_page_merger")
