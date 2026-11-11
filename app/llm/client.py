"""Compatibility alias for the shared generic model client."""
import importlib
import sys
sys.modules[__name__] = importlib.import_module("rag_service.llm.client")
