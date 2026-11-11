"""Existing-chunk reuse, empty indexes and pre-publication build failures."""
from copy import deepcopy
from unittest.mock import Mock

import numpy as np
import pytest

from app.rag.indexing.pipeline import IndexingPipeline
from app.rag.indexing.vector_store import FaissVectorStore
from app.rag.ingestion.pipeline import IngestionResult, IngestionPipeline
from app.rag.ingestion.docling_parser import DoclingParser
from app.rag.models import ChildChunk, DocumentRecord, ParentChunk


def existing_chunks():
    document = DocumentRecord(document_id="doc", filename="manual.md", file_type="md",
                              source_path="manual.md", checksum="checksum")
    parents = [ParentChunk(parent_id="p1", document_id="doc", content="First fact"),
               ParentChunk(parent_id="p2", document_id="doc", content="Second fact")]
    children = [ChildChunk(chunk_id=key, parent_id=parent.parent_id, document_id="doc",
                           source_name="manual.md", file_type="md", content=parent.content,
                           search_text="manual.md > Evidence\n" + parent.content, block_ids=[key + "-block"])
                for key, parent in zip(("c1", "c2"), parents)]
    return IngestionResult([document], parents, children)


def test_rebuild_existing_chunks_with_new_embeddings_without_parsing_or_saving(monkeypatch, tmp_path):
    monkeypatch.setattr(DoclingParser, "parse", Mock(side_effect=AssertionError("must not parse")))
    monkeypatch.setattr(IngestionPipeline, "run", Mock(side_effect=AssertionError("must not ingest")))
    monkeypatch.setattr(FaissVectorStore, "save", Mock(side_effect=AssertionError("memory only")))
    result = existing_chunks()
    original = deepcopy(result)
    texts = [child.search_text for child in result.children]
    embed_a = Mock(return_value=[[3., 0.], [0., 4.]])
    embed_b = Mock(return_value=[[0., 0., 2.], [0., 4., 0.]])
    factory = Mock(side_effect=FaissVectorStore)
    first = IndexingPipeline(embed_a, factory).build(result)
    second = IndexingPipeline(embed_b, factory).build(result)
    embed_a.assert_called_once_with(texts)
    embed_b.assert_called_once_with(texts)
    assert [call.args for call in factory.call_args_list] == [(2,), (3,)]
    assert first.store is not second.store
    assert first.store.index.d == 2 and second.store.index.d == 3
    assert first.store.records == second.store.records == [child.model_dump(mode="json") for child in result.children]
    assert first.documents == second.documents == result.documents
    assert first.parents == second.parents == result.parents
    assert result == original
    assert first.store.search([1., 0.], 1)[0]["chunk_id"] == "c1"
    assert second.store.search([0., 0., 1.], 1)[0]["chunk_id"] == "c1"
    assert np.allclose(np.linalg.norm(second.store.index.reconstruct_n(0, 2), axis=1), 1)
    assert list(tmp_path.iterdir()) == []


def test_empty_chunks_keep_existing_one_dimensional_format_without_embedding():
    embed = Mock(side_effect=AssertionError("empty index must not load or encode a model"))
    result = IngestionResult()
    snapshot = IndexingPipeline(embed).build(result)
    embed.assert_not_called()
    assert snapshot.store.index.d == 1
    assert snapshot.store.records == []
    assert snapshot.documents == snapshot.parents == []


@pytest.mark.parametrize("failure", ["embedding", "store_add"])
def test_index_build_failure_preserves_active_store_pipeline_and_disk_pointer(rag_factory, failure):
    (rag_factory.knowledge / "manual.md").write_text(
        "# Detection\n\nRepeated failed login attempts.", encoding="utf-8")
    retriever = rag_factory()
    previous_store, previous_pipeline = retriever.store, retriever.pipeline
    expected = retriever.search("failed login", 2)
    pointer = rag_factory.storage / "indexes/current.json"
    previous_pointer = pointer.read_bytes()
    if failure == "embedding":
        retriever.embedding_fn = Mock(side_effect=RuntimeError("embedding failed"))
    else:
        broken_store = Mock()
        broken_store.add.side_effect = RuntimeError("store add failed")
        retriever.store_factory = Mock(return_value=broken_store)
    with pytest.raises(RuntimeError, match="failed"):
        retriever.build_index(full=True)
    assert pointer.read_bytes() == previous_pointer
    assert retriever.store is previous_store
    assert retriever.pipeline is previous_pipeline
    assert retriever.search("failed login", 2) == expected
