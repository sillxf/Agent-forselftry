"""Build an in-memory vector index from existing chunks; no parsing or persistence."""
from dataclasses import dataclass

import numpy as np

from app.rag.indexing.vector_store import FaissVectorStore, VectorStoreInterface
from app.rag.ingestion.pipeline import IngestionResult
from app.rag.models import DocumentRecord, ParentChunk
from app.rag.views import validate_views


@dataclass
class IndexSnapshot:
    store: VectorStoreInterface
    documents: list[DocumentRecord]
    parents: list[ParentChunk]
    view_store: VectorStoreInterface | None = None
    view_model_name: str | None = None


class IndexingPipeline:
    def __init__(self, embed, store_factory=FaissVectorStore):
        self.embed = embed
        self.store_factory = store_factory

    def build(self, result: IngestionResult) -> IndexSnapshot:
        """Encode search_text in Child order and build a fresh, unpublished store."""
        records = [child.model_dump(mode="json") for child in result.children]
        if records:
            vectors = np.asarray(self.embed([record["search_text"] for record in records]), dtype="float32")
            store = self.store_factory(vectors.shape[1])
            store.add(vectors, records)
        else:
            # Preserve the existing empty-index format without loading an embedding model.
            store = self.store_factory(1)
        return IndexSnapshot(store, result.documents, result.parents)

    def build_views(self, snapshot: IndexSnapshot, views, *, model_name: str) -> IndexSnapshot:
        """Reuse original vectors/chunks; only encode the frozen auxiliary representations."""
        validate_views(views, snapshot.store.records)
        if not views:
            raise ValueError("Question views are empty")
        vectors = np.asarray(self.embed([view.search_text for view in views]), dtype="float32")
        if vectors.shape[1] != snapshot.store.dimension:
            raise ValueError("View embedding dimension differs from the original index")
        store = self.store_factory(vectors.shape[1])
        store.add(vectors, [dict(view.model_dump(mode="json"), chunk_id=view.view_id) for view in views])
        return IndexSnapshot(snapshot.store, snapshot.documents, snapshot.parents, store, model_name)
