"""Cache equivalence, invalidation, corruption recovery and reference-aware retention."""
import json
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest

from app.rag.indexing.embedding_cache import CachedEmbedder
from app.rag.indexing.maintenance import collect_generations


def test_unchanged_build_reuses_parsing_and_embeddings_without_changing_results(rag_factory):
    source = rag_factory.knowledge / "manual.md"
    source.write_text("# Detection\n\nRepeated failed login attempts.", encoding="utf-8")
    retriever = rag_factory(cache_enabled=True)
    original_document = retriever.documents[0]
    original_records = list(retriever.store.records)
    expected = retriever.search("login", 2)
    retriever.parser.parse = Mock(side_effect=AssertionError("cached document must not parse"))
    embed = Mock(wraps=retriever.embedding_fn)
    retriever.embedding_fn = embed
    retriever.build_index()
    assert retriever.documents[0] == original_document
    assert retriever.store.records == original_records
    assert retriever.registry.list_jobs()[0]["metrics"] == retriever.last_build_metrics
    assert retriever.last_build_metrics["artifact_cache_hits"] == 1
    assert retriever.last_build_metrics["parsed_documents"] == 0
    assert retriever.last_build_metrics["encoded_texts"] == 0
    embed.assert_not_called()
    # Query uses a live embedding function, not the build-time disk cache.
    assert [item["content"] for item in retriever.search("login", 2)] == [item["content"] for item in expected]


def test_only_changed_document_is_reparsed_and_reencoded(rag_factory):
    a, b = rag_factory.knowledge / "a.md", rag_factory.knowledge / "b.md"
    a.write_text("# A\n\nOriginal first evidence.", encoding="utf-8")
    b.write_text("# B\n\nOriginal second evidence.", encoding="utf-8")
    retriever = rag_factory(cache_enabled=True)
    parse = Mock(wraps=retriever.parser.parse)
    retriever.parser.parse = parse
    b.write_text("# B\n\nUpdated second evidence.", encoding="utf-8")
    retriever.build_index()
    assert parse.call_count == 1
    assert retriever.last_build_metrics["artifact_cache_hits"] == 1
    assert retriever.last_build_metrics["parsed_documents"] == 1
    assert retriever.last_build_metrics["embedding_cache_hits"] >= 1
    assert retriever.last_build_metrics["encoded_texts"] >= 1


def test_embedding_revision_invalidates_vectors_but_not_content_artifacts(rag_factory):
    (rag_factory.knowledge / "manual.md").write_text("# A\n\nEvidence.", encoding="utf-8")
    first = rag_factory(cache_enabled=True, embedding_cache_revision="one")
    previous = first.documents[0]
    second = rag_factory(cache_enabled=True, embedding_cache_revision="two")
    assert second.documents[0] == previous
    assert second.last_build_metrics["artifact_cache_hits"] == 1
    assert second.last_build_metrics["encoded_texts"] > 0


def test_corrupt_disposable_caches_are_regenerated_from_verified_sources(rag_factory):
    (rag_factory.knowledge / "manual.md").write_text("# A\n\nEvidence.", encoding="utf-8")
    retriever = rag_factory(cache_enabled=True)
    document = retriever.documents[0]
    (rag_factory.storage / "artifacts" / (document.artifact_id + ".json")).write_text("bad", encoding="utf-8")
    for path in (rag_factory.storage / "embedding_cache").glob("*.npz"):
        path.write_bytes(b"bad")
    retriever.build_index()
    assert retriever.last_build_metrics["parsed_documents"] == 1
    assert retriever.last_build_metrics["encoded_texts"] > 0
    assert retriever.search("evidence", 1)


def test_embedding_cache_deduplicates_batches_and_checks_dimensions(tmp_path):
    embed = Mock(return_value=[[1, 2]])
    cache = CachedEmbedder(embed, tmp_path, {"model": "one"})
    matrix = cache(["same", "same"])
    embed.assert_called_once_with(["same"])
    assert matrix.shape == (2, 2)
    again = CachedEmbedder(Mock(side_effect=AssertionError("cache hit")), tmp_path, {"model": "one"})
    assert np.array_equal(again(["same"]), [[1, 2]])
    mixed = CachedEmbedder(Mock(return_value=[[1, 2, 3]]), tmp_path, {"model": "one"})
    with pytest.raises(ValueError, match="dimensions differ"):
        mixed(["same", "new"])


def test_gc_preserves_current_previous_and_all_retained_cache_references(rag_factory):
    source = rag_factory.knowledge / "manual.md"
    source.write_text("# A\n\nVersion 0.", encoding="utf-8")
    retriever = rag_factory(cache_enabled=True)
    document_id = retriever.documents[0].document_id
    for index in range(1, 5):
        source.write_text(f"# A\n\nVersion {index}.", encoding="utf-8")
        retriever.build_index()
    current = retriever.repository.current_pointer()["generation"]
    previous = json.loads((retriever.repository.root / "previous.json").read_text(encoding="utf-8"))["generation"]
    outcome = collect_generations(retriever.build_service, keep=2, min_age_seconds=0)
    assert len(outcome["generations"]) == 3
    assert outcome["artifacts"] and outcome["embeddings"]
    for generation in (current, previous):
        snapshot = retriever.repository.load_generation(generation)
        for document in snapshot.documents:
            assert (rag_factory.storage / "artifacts" / (document.artifact_id + ".json")).exists()
        for key in snapshot.embedding_cache_keys:
            assert (rag_factory.storage / "embedding_cache" / (key + ".npz")).exists()
    assert len(retriever.registry.list_versions(document_id)) == 5
    assert all(Path(version.source_blob_path).exists() for version in retriever.registry.list_versions(document_id))
    assert retriever.search("version", 1)
    with pytest.raises(ValueError, match="at least two"):
        collect_generations(retriever.build_service, keep=1)


def test_gc_respects_an_active_cold_load_lease(rag_factory):
    from filelock import FileLock
    source = rag_factory.knowledge / "manual.md"
    source.write_text("# A\n\nVersion 0.", encoding="utf-8")
    retriever = rag_factory(cache_enabled=True)
    old = retriever.repository.current_pointer()["generation"]
    for index in range(1, 4):
        source.write_text(f"# A\n\nVersion {index}.", encoding="utf-8")
        retriever.build_index()
    with FileLock(str(retriever.repository.root / f".read-{old}.lock"), timeout=0):
        outcome = collect_generations(retriever.build_service, keep=2, min_age_seconds=0)
        assert old not in outcome["generations"]
        assert (retriever.repository.root / old).exists()
    outcome = collect_generations(retriever.build_service, keep=2, min_age_seconds=0)
    assert old in outcome["generations"]
