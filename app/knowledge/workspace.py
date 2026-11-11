"""Per-KB storage handles; no model, query, or indexing orchestration."""

from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from uuid import UUID
from filelock import FileLock
from app.knowledge.repository import DocumentRegistry
from app.knowledge.lifecycle import LifecycleService
from app.storage.snapshot_repository import SnapshotRepository


@dataclass(frozen=True)
class Workspace:
    knowledge_dir: Path
    storage_dir: Path
    registry: DocumentRegistry
    lifecycle: LifecycleService
    repository: SnapshotRepository


class Workspaces:
    def __init__(self, root, knowledge_base):
        self.root, self.knowledge_base = Path(root), knowledge_base
        self._items, self._gates, self._lock = {}, {}, RLock()

    def maintenance_lock(self, kb_id):
        if UUID(kb_id).hex != kb_id:
            raise ValueError("Invalid knowledge base identifier")
        with self._lock:
            if kb_id not in self._gates:
                locks = self.root / "locks"
                locks.mkdir(parents=True, exist_ok=True)
                self._gates[kb_id] = FileLock(str(locks / (kb_id + ".lock")), timeout=0)
            return self._gates[kb_id]

    def get(self, kb_id):
        with self._lock:
            self.knowledge_base(kb_id)
            if kb_id not in self._items:
                base = self.root / "bases" / kb_id
                knowledge, storage = base / "knowledge", base / "storage"
                if not knowledge.is_dir():
                    with self.maintenance_lock(kb_id):
                        self.knowledge_base(kb_id)
                        knowledge.mkdir(parents=True, exist_ok=True)
                registry = DocumentRegistry(
                    storage, access_guard=lambda: self.knowledge_base(kb_id)
                )
                self._items[kb_id] = Workspace(
                    knowledge,
                    storage,
                    registry,
                    LifecycleService(storage, registry),
                    SnapshotRepository(storage),
                )
            return self._items[kb_id]

    def discard(self, kb_id):
        with self._lock:
            self._items.pop(kb_id, None)
