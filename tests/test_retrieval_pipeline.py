"""Focused composition, Parent deduplication and index-snapshot checks."""
from unittest.mock import Mock

import pytest

from app.rag.models import ParentChunk
from app.rag.retrieval.context import ParentContextBuilder
from app.rag.retrieval.fusion import RRFFusion
from app.rag.retrieval.pipeline import RetrievalPipeline


def candidate(key, parent_id, **scores):
    return dict(chunk_id=key, parent_id=parent_id, document_id="doc", source_name="manual.md",
                content=key, page_start=1, page_end=1, block_ids=[key], **scores)


def test_components_are_replaceable_and_parent_topk_is_independent_of_child_topk():
    a, b, c = [candidate(key, parent, dense_score=score)
               for key, parent, score in [("a", "p1", .9), ("b", "p1", .8), ("c", "p2", .7)]]
    parents = {key: ParentChunk(parent_id=key, document_id="doc", content="Full " + key)
               for key in ("p1", "p2")}
    dense = Mock(); dense.retrieve.return_value = [a, b, c]
    sparse = Mock(); sparse.retrieve.return_value = [dict(a, sparse_score=2.0)]
    pipeline = RetrievalPipeline(dense, sparse, RRFFusion(), ParentContextBuilder(parents),
                                 dense_top_k=7, bm25_top_k=9)
    result = pipeline.search_rankings("query", 2)
    dense.retrieve.assert_called_once_with("query", 8)
    sparse.retrieve.assert_called_once_with("query", 9)
    assert [r["chunk_id"] for r in result["children"]] == ["a", "b"]
    assert [r["parent_id"] for r in result["parents"]] == ["p1", "p2"]
    assert result["candidate_count"] == 3
    hit = result["children"][0]
    assert hit["dense_score"] == .9 and hit["sparse_score"] == 2.0
    assert hit["score"] == 2 / 61
    assert result["parents"][0]["content"] == "Full p1"
    sparse.retrieve.reset_mock()
    assert pipeline.rank_candidates("query", 2, "dense") == [a, b, c]
    sparse.retrieve.assert_not_called()
    assert pipeline.search_rankings(" ", 2) == dict(children=[], parents=[], candidate_count=0)
    assert pipeline.search_rankings("query", 0) == dict(children=[], parents=[], candidate_count=0)
    with pytest.raises(ValueError, match="Unknown retrieval strategy"):
        pipeline.rank_candidates("query", 2, "invalid")


def test_rrf_supports_multiple_routes_without_mutating_inputs_or_losing_scores():
    a = candidate("a", "p1", dense_score=.5)
    sparse_a = dict(a, sparse_score=3.0)
    b = candidate("b", "p2", dense_score=.6)
    rankings = [[a, a], [sparse_a], [b]]
    fused = RRFFusion().fuse(rankings)
    assert [r["chunk_id"] for r in fused] == ["a", "b"]
    assert fused[0]["score"] == 2 / 61
    assert fused[0]["dense_score"] == .5 and fused[0]["sparse_score"] == 3.0
    assert "score" not in a and "sparse_score" not in a
    assert RRFFusion().fuse([[a], [b]])[0]["chunk_id"] == "b"


def test_rebuild_rebinds_dense_sparse_and_context_to_one_new_snapshot(rag_factory):
    source = rag_factory.knowledge / "manual.md"
    source.write_text("# Detection\n\nRepeated failed login attempts.", encoding="utf-8")
    retriever = rag_factory()
    previous = retriever.pipeline
    old_parent_ids = set(retriever.parents)
    source.write_text("# Response\n\nReplacement protocol for isolation.", encoding="utf-8")
    retriever.build_index()
    current = retriever.pipeline
    assert current is not previous
    assert current.dense.store is retriever.store
    assert current.sparse.records is retriever.store.records
    assert current.context_builder.parents is retriever.parents
    assert current.sparse.retrieve("failed", 5) == []
    assert previous.sparse.retrieve("failed", 5)
    assert current.search_rankings("replacement", 2)["parents"]
    assert set(retriever.parents).isdisjoint(old_parent_ids)
