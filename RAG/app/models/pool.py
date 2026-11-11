"""Bounded per-process model ownership and per-operation usage."""

from collections import OrderedDict
from contextlib import contextmanager
from contextvars import ContextVar
from threading import RLock
from time import monotonic
import os

from app.core.exceptions import BusyError

usage_context = ContextVar("model_usage", default=None)


class _Loaded:
    def __init__(self, model):
        self.model, self.lock, self.users = model, RLock(), 0


class ModelPool:
    """Loading and eviction are serialized; inference is serialized per model.

    One lock for everything let a slow CPU rerank (seconds) block every query
    embedding behind it, and those requests failed with 503. A model in use is
    never evicted, so a reload cannot put a second copy in memory.
    """

    def __init__(self, max_loaded=3):
        if not 1 <= max_loaded <= 16:
            raise ValueError("Model pool size must be between 1 and 16")
        self.max_loaded = max_loaded
        self.models = OrderedDict()
        self.lock = RLock()

    @contextmanager
    def use(self, key, factory):
        timeout = float(os.getenv("RAG_MODEL_ACQUIRE_TIMEOUT_SECONDS", "5"))
        deadline = monotonic() + timeout
        if not self.lock.acquire(timeout=timeout):
            # BusyError maps to 503 "busy"; TimeoutError is an OSError and was
            # reported as a storage failure.
            raise BusyError("Local model capacity is busy; retry later")
        try:
            entry = self.models.get(key)
            if entry is None:
                while len(self.models) >= self.max_loaded:
                    idle = next(
                        (k for k, e in self.models.items() if e.users == 0), None
                    )
                    if idle is None:
                        raise BusyError("All loaded models are in use; retry later")
                    del self.models[idle]
                entry = self.models[key] = _Loaded(factory())
            self.models.move_to_end(key)
            entry.users += 1
        finally:
            self.lock.release()
        try:
            if not entry.lock.acquire(timeout=max(0.0, deadline - monotonic())):
                raise BusyError("Local model capacity is busy; retry later")
            try:
                yield entry.model
            finally:
                entry.lock.release()
        finally:
            with self.lock:
                entry.users -= 1
