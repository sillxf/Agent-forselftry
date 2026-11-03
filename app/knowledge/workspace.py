"""Per-KB storage handles; no model, query, or indexing orchestration."""

from dataclasses import dataclass
from pathlib import Path
from threading import RLock
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
        self._items, self._lock = {}, RLock()

    def get(self, kb_id):
        self.knowledge_base(kb_id)
        with self._lock:
            if kb_id not in self._items:
                base = self.root / "bases" / kb_id
                knowledge, storage = base / "knowledge", base / "storage"
                knowledge.mkdir(parents=True, exist_ok=True)
                registry = DocumentRegistry(storage)
                self._items[kb_id] = Workspace(
                    knowledge,
                    storage,
                    registry,
                    LifecycleService(storage, registry),
                    SnapshotRepository(storage),
                )
            return self._items[kb_id]
