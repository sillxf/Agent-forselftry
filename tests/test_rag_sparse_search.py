"""Sparse-search parity and candidate-only scoring, without parsing or models."""
from unittest.mock import Mock

import pytest

from app.rag.retrieval.sparse import SparseRetriever, tokenize


@pytest.fixture
def retriever():
    return SparseRetriever([
        {"chunk_id": "z", "search_text": "failed login CVE-2025-12345 中文告警"},
        {"chunk_id": "a", "search_text": "failed login CVE-2025-12345 中文告警"},
        {"chunk_id": "other", "search_text": "isolate host malware 192.168.1.10"},
        {"chunk_id": "repeated", "search_text": "login login login mitigation"},
        {"chunk_id": "punctuation", "search_text": "!!!"},
    ])


@pytest.mark.parametrize("query", [
    "failed login", "login login failed", "CVE-2025-12345", "192.168.1.10",
    "中文告警", "中文 login", "missing", "!!!", "",
])
@pytest.mark.parametrize("limit", [1, 3, 20])
def test_sparse_search_matches_exhaustive_scores_and_order(retriever, query, limit):
    tokens = tokenize(query)
    scores = retriever.bm25.get_scores(tokens)
    matches = [index for index, record in enumerate(retriever.records)
               if set(tokens) & set(tokenize(record["search_text"]))]
    matches.sort(key=lambda index: -float(scores[index]))
    expected = [{**retriever.records[index], "sparse_score": float(scores[index])}
                for index in matches[:limit]]
    assert retriever.retrieve(query, limit) == expected


def test_sparse_search_scores_only_candidates_and_keeps_repeated_query_terms(retriever):
    retriever.bm25.get_scores = Mock(side_effect=AssertionError("must not score the whole corpus"))
    retriever.bm25.get_batch_scores = Mock(wraps=retriever.bm25.get_batch_scores)
    retriever.retrieve("failed failed", 20)
    retriever.bm25.get_batch_scores.assert_called_once_with(["failed", "failed"], [0, 1])
    retriever.bm25.get_batch_scores.reset_mock()
    assert retriever.retrieve("missing", 20) == []
    retriever.bm25.get_batch_scores.assert_not_called()


def test_sparse_search_keeps_corpus_order_for_ties(retriever):
    results = retriever.retrieve("failed", 20)
    assert [item["chunk_id"] for item in results] == ["z", "a"]
    assert results[0]["sparse_score"] == results[1]["sparse_score"]


def test_new_sparse_snapshot_does_not_reuse_old_postings(retriever):
    replacement = SparseRetriever([{"chunk_id": "new", "search_text": "replacement"}])
    assert replacement.retrieve("failed", 20) == []
    assert replacement.retrieve("replacement", 20)[0]["chunk_id"] == "new"
    assert retriever.retrieve("failed", 20)
    empty = SparseRetriever([])
    assert empty.postings == {}
    assert empty.retrieve("replacement", 20) == []
