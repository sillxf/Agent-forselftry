"""Sparse-search parity and candidate-only scoring, without parsing or models."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.rag.retriever import KnowledgeRetriever, tokenize


@pytest.fixture
def retriever():
    retriever = KnowledgeRetriever(build=False)
    retriever.store = SimpleNamespace(records=[
        {"chunk_id": "z", "search_text": "failed login CVE-2025-12345 中文告警"},
        {"chunk_id": "a", "search_text": "failed login CVE-2025-12345 中文告警"},
        {"chunk_id": "other", "search_text": "isolate host malware 192.168.1.10"},
        {"chunk_id": "repeated", "search_text": "login login login mitigation"},
        {"chunk_id": "punctuation", "search_text": "!!!"},
    ])
    retriever._build_sparse()
    return retriever


@pytest.mark.parametrize("query", [
    "failed login", "login login failed", "CVE-2025-12345", "192.168.1.10",
    "中文告警", "中文 login", "missing", "!!!", "",
])
@pytest.mark.parametrize("limit", [1, 3, 20])
def test_sparse_search_matches_exhaustive_scores_and_order(retriever, query, limit):
    tokens = tokenize(query)
    scores = retriever._bm25.get_scores(tokens)
    matches = [index for index, record in enumerate(retriever.store.records)
               if set(tokens) & set(tokenize(record["search_text"]))]
    matches.sort(key=lambda index: -float(scores[index]))
    expected = [{**retriever.store.records[index], "sparse_score": float(scores[index])}
                for index in matches[:limit]]
    assert retriever._sparse_search(query, limit) == expected


def test_sparse_search_scores_only_candidates_and_keeps_repeated_query_terms(retriever):
    retriever._bm25.get_scores = Mock(side_effect=AssertionError("must not score the whole corpus"))
    retriever._bm25.get_batch_scores = Mock(wraps=retriever._bm25.get_batch_scores)
    retriever._sparse_search("failed failed", 20)
    retriever._bm25.get_batch_scores.assert_called_once_with(["failed", "failed"], [0, 1])
    retriever._bm25.get_batch_scores.reset_mock()
    assert retriever._sparse_search("missing", 20) == []
    retriever._bm25.get_batch_scores.assert_not_called()


def test_sparse_search_keeps_corpus_order_for_ties(retriever):
    results = retriever._sparse_search("failed", 20)
    assert [item["chunk_id"] for item in results] == ["z", "a"]
    assert results[0]["sparse_score"] == results[1]["sparse_score"]


def test_rebuilding_sparse_index_replaces_old_postings(retriever):
    retriever.store.records = [{"chunk_id": "new", "search_text": "replacement"}]
    retriever._build_sparse()
    assert retriever._sparse_search("failed", 20) == []
    assert retriever._sparse_search("replacement", 20)[0]["chunk_id"] == "new"
    retriever.store.records = []
    retriever._build_sparse()
    assert retriever._postings == {}
    assert retriever._sparse_search("replacement", 20) == []
