"""Experimental query routes over frozen chunks; never changes production defaults."""
from app.rag.embedder import embed_texts
from app.rag.retriever import reciprocal_rank_fusion


def fuse_query_rankings(rankings, rank_constant=60):
    """Equal-weight query RRF; deduplicate by chunk identity, never sum raw scores."""
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
    routes = []
    for query in queries:
        if store is None:
            ranked = retriever._rank_children(query, top_k, strategy)
        else:
            dense = store.search(embed_texts([query], model_name)[0], max(retriever.dense_top_k, top_k * 4)) if strategy != "bm25" else []
            sparse = retriever._sparse_search(query, max(retriever.bm25_top_k, top_k * 4)) if strategy != "dense" else []
            ranked = reciprocal_rank_fusion(dense, sparse) if strategy == "hybrid" else (dense if strategy == "dense" else sparse)
        routes.append(ranked)
    ranked = routes[0] if len(routes) == 1 else fuse_query_rankings(routes)
    return {"children": [dict(r, source_block_ids=r["block_ids"]) for r in ranked[:top_k]],
            "parents": retriever._restore_parents(ranked, top_k),
            "candidate_count": len(ranked),
            "route_candidates": [{"query": query, "chunk_ids": [r["chunk_id"] for r in route]}
                                 for query, route in zip(queries, routes)]}
