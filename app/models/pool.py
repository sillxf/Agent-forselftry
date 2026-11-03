"""Bounded per-process model ownership and per-operation usage."""

from collections import OrderedDict
from contextlib import contextmanager
from contextvars import ContextVar
from threading import RLock
import os

usage_context = ContextVar("model_usage", default=None)


class ModelPool:
    def __init__(self, max_loaded=3):
        if not 1 <= max_loaded <= 16:
            raise ValueError("Model pool size must be between 1 and 16")
        self.max_loaded = max_loaded
        self.models = OrderedDict()
        self.lock = RLock()

    @contextmanager
    def use(self, key, factory):
        # Serialized local inference bounds both VRAM loading and concurrent inference.
        if not self.lock.acquire(
            timeout=float(os.getenv("RAG_MODEL_ACQUIRE_TIMEOUT_SECONDS", "5"))
        ):
            raise TimeoutError("Local model capacity is busy")
        try:
            if key not in self.models:
                while len(self.models) >= self.max_loaded:
                    self.models.popitem(last=False)
                self.models[key] = factory()
            self.models.move_to_end(key)
            yield self.models[key]
        finally:
            self.lock.release()
