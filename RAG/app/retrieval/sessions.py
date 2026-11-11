"""Read-only sessions: never build, mutate source records or publish."""

from collections import OrderedDict
from threading import RLock
import json
from app.core.contracts import RetrievalProfile
from app.core.exceptions import NotPublished
from app.retrieval.orchestrator import RetrievalOrchestrator


class QuerySession:
    def __init__(self, workspace, factory, profile, reranker):
        self.workspace, self.factory = workspace, factory
        self.orchestrator = RetrievalOrchestrator(profile, reranker_factory=reranker)
        self._pipeline, self._generation, self._lock = None, None, RLock()

    @property
    def pipeline(self):
        with self._lock:
            pointer = self.workspace.repository.current_pointer()
            if not pointer:
                raise NotPublished("No published index; submit an explicit build first")
            if pointer["generation"] != self._generation:
                # Shared read-only copy: document and chunk reads reuse it.
                snapshot = self.workspace.repository.load_generation(
                    pointer["generation"], cached=True
                )
                pipeline = self.factory.create(
                    snapshot, pointer["signature"]["model"], self.workspace.registry
                )
                pipeline.generation_id = pointer["generation"]
                self._pipeline, self._generation = pipeline, pointer["generation"]
            return self._pipeline


class QuerySessions:
    def __init__(self, bases, workspaces, factory, providers):
        self.bases, self.workspaces, self.factory, self.providers = (
            bases,
            workspaces,
            factory,
            providers,
        )
        self._items, self._lock = OrderedDict(), RLock()

    def get(self, kb_id):
        configuration = self.bases.kb(kb_id)
        key = (kb_id, json.dumps(configuration["profile"], sort_keys=True))
        with self._lock:
            if key not in self._items:
                profile = RetrievalProfile.model_validate(
                    configuration["profile"]
                ).model_copy(
                    update={
                        "reranker_model": "provider:"
                        + configuration["profile"]["reranker_id"]
                    }
                )
                self._items[key] = QuerySession(
                    self.workspaces.get(kb_id),
                    self.factory,
                    profile,
                    lambda: self.providers.reranker("provider:" + profile.reranker_id),
                )
                while len(self._items) > 8:
                    self._items.popitem(last=False)
            self._items.move_to_end(key)
            return self._items[key]

    def discard(self, kb_id):
        with self._lock:
            for key in [key for key in self._items if key[0] == kb_id]:
                del self._items[key]
