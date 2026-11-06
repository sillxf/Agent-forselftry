"""Caller-directed retrieval, bounded reranking and canonical-evidence fallbacks."""

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from copy import deepcopy
from math import isfinite
from threading import Lock
from time import perf_counter

from app.retrieval.fusion import RRFFusion
from app.core.exceptions import InvalidRequest
from app.retrieval.policy import RetrievalPolicy


class RetrievalOrchestrator:
    def __init__(self, policy=None, *, reranker_factory=None):
        self.policy = policy or RetrievalPolicy()
        self._factory = reranker_factory
        self._reranker = None
        self._reranker_model = None
        self._executor = None
        self._running = 0
        self._lock = Lock()

    def _adapter(self, model):
        """Caller holds the lock. Creating an adapter is cheap; models load on use."""
        if self._reranker is None or self._reranker_model != model:
            if self._factory is None:
                raise ValueError("No reranker adapter is configured")
            self._reranker, self._reranker_model = self._factory(), model
            if self._executor is not None:
                self._executor.shutdown(wait=False)
                self._executor = None
        return self._reranker

    def _run(self, reranker, query, candidates):
        try:
            return reranker.rerank(query, candidates)
        finally:
            with self._lock:
                self._running -= 1

    def _bounded_rerank(self, query, ranked, policy):
        with self._lock:
            try:
                reranker = self._adapter(policy.reranker_model)
            except Exception as exc:  # Ranking falls back; never fail the search.
                return ranked, "reranker_error:" + type(exc).__name__
            # A local cross-encoder runs one at a time; a remote service may take more.
            limit = max(1, int(getattr(reranker, "concurrency", 1)))
            if self._running >= limit:
                return ranked, "reranker_busy"
            if self._executor is None:
                self._executor = ThreadPoolExecutor(
                    max_workers=limit, thread_name_prefix="rag-rerank"
                )
            self._running += 1
            future = self._executor.submit(self._run, reranker, query, deepcopy(ranked))
        try:
            output = future.result(timeout=policy.reranker_timeout_seconds)
            originals = {item["chunk_id"]: item for item in ranked}
            keys = [item["chunk_id"] for item in output]
            if len(keys) != len(originals) or set(keys) != set(originals):
                raise ValueError("Reranker changed the candidate identities")
            if any(
                "reranker_score" in item and not isfinite(float(item["reranker_score"]))
                for item in output
            ):
                raise ValueError("Reranker produced a nonfinite score")
            # Optional components may reorder/score, never replace the original evidence.
            return [
                dict(
                    originals[item["chunk_id"]],
                    **(
                        {"reranker_score": item["reranker_score"]}
                        if "reranker_score" in item
                        else {}
                    ),
                )
                for item in output
            ], None
        except TimeoutError:
            return ranked, "reranker_timeout"
        except Exception as exc:
            return ranked, "reranker_error:" + type(exc).__name__

    def search(self, retriever, query, k, *, supplement=False, extra_queries=()):
        started = perf_counter()
        policy = self.policy
        if any(len(q) > policy.max_query_chars for q in [query, *extra_queries]):
            raise InvalidRequest("Knowledge query exceeds the configured character budget")
        k = min(k, policy.max_top_k)
        trace = {
            "strategy": policy.default_strategy,
            "reranker_used": False,
            "fallback_reason": None,
            "multi_view": "not_requested" if policy.multi_view_enabled else "disabled",
            "supplement_requested": supplement,
            "supplement_passes": 0,
            "query_count": 1 + len(extra_queries),
        }
        if not query.strip() or k <= 0:
            return {
                "results": [],
                "trace": dict(
                    trace, elapsed_ms=0, context_tokens=0, candidate_count=0
                ),
            }
        pipeline = (
            retriever.pipeline
        )  # Pin one complete generation for both retrieval routes.
        use_reranker = policy.default_strategy == "hybrid_rerank"
        retrieval_started = perf_counter()
        ranked = pipeline.rank_candidates(
            query,
            k,
            "hybrid"
            if policy.default_strategy == "hybrid_rerank"
            else policy.default_strategy,
            candidate_k=policy.candidate_k if use_reranker else None,
            extra_queries=extra_queries,
        )
        trace["retrieval_elapsed_ms"] = (perf_counter() - retrieval_started) * 1000
        trace["before_rerank"] = [
            {
                "chunk_id": x["chunk_id"],
                "dense_score": x.get("dense_score"),
                "sparse_score": x.get("sparse_score"),
                "fusion_score": x.get("score"),
            }
            for x in ranked[:100]
        ]
        ranking_started = perf_counter()
        if use_reranker and ranked:
            ranked, error = self._bounded_rerank(query, ranked, policy)
            trace.update(reranker_used=error is None, fallback_reason=error)
        trace["rerank_elapsed_ms"] = (perf_counter() - ranking_started) * 1000
        trace["after_rerank"] = [
            {"chunk_id": x["chunk_id"], "reranker_score": x.get("reranker_score")}
            for x in ranked[:100]
        ]
        primary = ranked
        if supplement:
            if not policy.multi_view_enabled:
                trace["fallback_reason"] = "multi_view_disabled"
            elif pipeline.multi_view_dense is None:
                trace["fallback_reason"] = "multi_view_unavailable"
            else:
                supplemental_started = perf_counter()
                try:
                    trace["supplement_passes"] = 1
                    extra = pipeline.rank_candidates(
                        query,
                        k,
                        "multi_view",
                        candidate_k=policy.supplement_candidate_k,
                    )
                    base = primary[: policy.candidate_k]
                    merged = RRFFusion().fuse([base, extra])
                    trace["added_candidates"] = len(
                        {r["chunk_id"] for r in extra} - {r["chunk_id"] for r in base}
                    )
                    if merged:
                        reranked, error = self._bounded_rerank(query, merged, policy)
                        if error:
                            trace["fallback_reason"] = error
                        else:
                            ranked = reranked
                            trace.update(
                                reranker_used=True,
                                fallback_reason=None,
                                multi_view="used",
                            )
                    else:
                        trace["multi_view"] = "empty"
                except Exception as exc:
                    ranked = primary
                    trace["fallback_reason"] = "supplement_error:" + type(exc).__name__
                trace["supplement_elapsed_ms"] = (
                    perf_counter() - supplemental_started
                ) * 1000
        if pipeline.eligibility is not None:
            allowed = pipeline.eligibility()
            ranked = [item for item in ranked if item["document_id"] in allowed]
        results, used = [], 0
        for item in pipeline.context_builder.build(ranked, k):
            item = dict(item, context_scope="parent")
            if not policy.parent_context:
                item = as_child(item)
            tokens = pipeline.count_tokens(item)
            if used + tokens > policy.max_context_tokens and item["context_scope"] != "child":
                # Over budget: fall back to the matched Child instead of dropping the hit.
                item = as_child(item)
                tokens = pipeline.count_tokens(item)
            if used + tokens <= policy.max_context_tokens:
                results.append(dict(item, context_tokens=tokens))
                used += tokens
        trace.update(
            generation_id=getattr(pipeline, "generation_id", None),
            candidate_count=len(ranked),
            context_tokens=used,
            returned_parents=len(results),
            elapsed_ms=(perf_counter() - started) * 1000,
        )
        return {"results": results, "trace": trace}


def as_child(item):
    return dict(
        item,
        content=item["chunk_content"],
        context_scope="child",
        page_start=item["matched_page_start"],
        page_end=item["matched_page_end"],
    )
