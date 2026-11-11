from unittest.mock import Mock

from evaluation.rag.reranker_multiview_supplement_experiment import MultiViewSupplementRanker


def test_multiview_supplement_excludes_hybrid_hits_and_keeps_canonical_children():
    original = [
        {"chunk_id": "a", "parent_id": "p1", "block_ids": ["a"], "content": "A", "source_name": "x"},
    ]
    view_hits = [
        {"chunk_id": "view-a", "view_id": "view-a", "source_child_id": "a", "dense_score": .9},
        {"chunk_id": "view-b", "view_id": "view-b", "source_child_id": "b", "dense_score": .8},
    ]
    pipeline = Mock()
    pipeline.rank_candidates.return_value = original
    pipeline.dense.embed.return_value = [[1.0]]
    retriever = Mock(pipeline=pipeline, store=Mock(records=[*original,
        {"chunk_id": "b", "parent_id": "p2", "block_ids": ["b"], "content": "B", "source_name": "x"}]))
    reranker = Mock()
    reranker.rerank.side_effect = lambda query, candidates: candidates
    view_store = Mock()
    view_store.search.return_value = view_hits

    ranker = MultiViewSupplementRanker(retriever, view_store, reranker, candidate_k=1,
                                        view_top_k=2, max_supplement=2)
    ranker("query", 1, "hybrid_multiview_supplement_bge_reranker")

    reranked_candidates = reranker.rerank.call_args.args[1]
    assert [item["chunk_id"] for item in reranked_candidates] == ["a", "b"]
    assert reranked_candidates[0]["candidate_origin"] == "hybrid"
    assert reranked_candidates[1]["candidate_origin"] == "multiview_supplement"
    assert ranker.details[0]["supplement_child_ids"] == ["b"]
