"""Only experiment routing/fusion is new; production retrieval is left unchanged."""
from app.rag.evaluation.crosslingual import fuse_query_rankings, rank_experiment


def test_query_fusion_deduplicates_without_using_incomparable_raw_scores():
    a = dict(chunk_id="a", dense_score=100)
    b = dict(chunk_id="b", dense_score=-1)
    c = dict(chunk_id="c", dense_score=500)
    ranked = fuse_query_rankings([[a, b, a], [b, c]])
    assert [r["chunk_id"] for r in ranked] == ["b", "a", "c"]
    assert ranked[0]["score"] == 1/62 + 1/61
    assert ranked[1]["score"] == 1/61


def test_dual_query_preserves_routes_and_restores_unique_parents(rag_factory):
    (rag_factory.knowledge / "manual.md").write_text("# Detection\n\nFailed login evidence.\n\n# Response\n\nBlock the source.",encoding="utf8")
    retriever = rag_factory()
    result = rank_experiment(retriever,["failed login","block source"],"hybrid",2)
    assert [r["query"] for r in result["route_candidates"]] == ["failed login","block source"]
    assert len({r["chunk_id"] for r in result["children"]}) == 2
    assert len({r["parent_id"] for r in result["parents"]}) == 2
    assert len(result["parents"]) == len(result["children"]) == 2
