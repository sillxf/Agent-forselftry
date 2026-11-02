"""Build an in-memory vector index from existing chunks; no parsing or persistence."""
from dataclasses import dataclass

import numpy as np

from app.rag.indexing.vector_store import FaissVectorStore, VectorStoreInterface
from app.rag.ingestion.pipeline import IngestionResult
from app.rag.models import DocumentRecord, ParentChunk


@dataclass
class IndexSnapshot:
    store: VectorStoreInterface
    documents: list[DocumentRecord]
    parents: list[ParentChunk]


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
