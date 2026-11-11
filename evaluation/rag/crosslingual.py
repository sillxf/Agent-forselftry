"""Experimental query routes over frozen chunks; never changes production defaults."""
from functools import partial

from app.rag.embedder import embed_texts

from app.rag.retrieval.dense import DenseRetriever
from app.rag.retrieval.pipeline import RetrievalPipeline


def fuse_query_rankings(rankings, rank_constant=60):
    """Legacy query-level policy: first-route metadata and ID-only tie breaking.

    Intentionally differs from production score-tied RRF; retain historical ranks.
    """
    scores, records = {}, {}
    for ranked in rankings:
        seen = set()
        for rank, record in enumerate(ranked, 1):
            key = record["chunk_id"]
            if key in seen:
                continue
            seen.add(key)
            scores[key] = scores.get(key, 0.0) + 1 / (rank_constant + rank)
            records.setdefault(key, record)
    keys = sorted(scores, key=lambda key: (-scores[key], key))
    return [{**records[key], "score": scores[key]} for key in keys]


def rank_experiment(retriever, queries, strategy, top_k, *, model_name=None, store=None):
    pipeline = retriever.pipeline
    if store is not None:
        pipeline = RetrievalPipeline(
            DenseRetriever(store, partial(embed_texts, model_name=model_name)),
            pipeline.sparse, pipeline.fusion, pipeline.context_builder,
            dense_top_k=pipeline.dense_top_k, bm25_top_k=pipeline.bm25_top_k,
        )
    routes = [pipeline.rank_candidates(query, top_k, strategy) for query in queries]
    ranked = routes[0] if len(routes) == 1 else fuse_query_rankings(routes)
    return {"children": [dict(r, source_block_ids=r["block_ids"]) for r in ranked[:top_k]],
            "parents": pipeline.context_builder.build(ranked, top_k),
            "candidate_count": len(ranked),
            "route_candidates": [{"query": query, "chunk_ids": [r["chunk_id"] for r in route]}
                                 for query, route in zip(queries, routes)]}
