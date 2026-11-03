"""Primary retrieval policy, bounded optional reranking and per-request diagnostics."""
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from copy import deepcopy
from math import isfinite
from threading import Lock
from time import perf_counter

from app.rag.retrieval.policy import RetrievalPolicy


class RetrievalOrchestrator:
    def __init__(self, policy=None, *, reranker_factory=None):
        self.policy = policy or RetrievalPolicy()
        self._factory = reranker_factory
        self._reranker = None
        self._executor = None
        self._future = None
        self._lock = Lock()

    def _rerank(self, query, candidates):
        if self._reranker is None:
            if self._factory is not None:
                self._reranker = self._factory()
            else:
                from app.rag.retrieval.reranker import BGEReranker
                self._reranker = BGEReranker(self.policy.reranker_model)
        return self._reranker.rerank(query, candidates)

    def search(self, retriever, query, k):
        started = perf_counter()
        if len(query) > self.policy.max_query_chars:
            raise ValueError("Knowledge query exceeds the configured character budget")
        k = min(k, self.policy.max_top_k)
        trace = {"strategy": self.policy.default_strategy, "reranker_used": False,
                 "fallback_reason": None, "multi_view": "disabled_unvalidated"}
        if not query.strip() or k <= 0:
            return {"results": [], "trace": dict(trace, elapsed_ms=0, context_chars=0, candidate_count=0)}
        pipeline = retriever.pipeline  # One immutable runtime is pinned for the whole request.
        use_reranker = self.policy.default_strategy == "hybrid_rerank"
        ranked = pipeline.rank_candidates(query, k, "hybrid", candidate_k=self.policy.candidate_k if use_reranker else None)
        if use_reranker and ranked:
            with self._lock:
                if self._future is not None and not self._future.done():
                    future = None
                    trace["fallback_reason"] = "reranker_busy"
                else:
                    if self._executor is None:
                        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="rag-rerank")
                    self._future = self._executor.submit(self._rerank, query, deepcopy(ranked))
                    future = self._future
            if future is not None:
                try:
                    output = future.result(timeout=self.policy.reranker_timeout_seconds)
                    originals = {item["chunk_id"]: item for item in ranked}
                    keys = [item["chunk_id"] for item in output]
                    if len(keys) != len(originals) or set(keys) != set(originals):
                        raise ValueError("Reranker changed the candidate identities")
                    if any("reranker_score" in item and not isfinite(float(item["reranker_score"])) for item in output):
                        raise ValueError("Reranker produced a nonfinite score")
                    # Only ordering and score come from the optional component, never evidence text.
                    ranked = [dict(originals[item["chunk_id"]], **(
                        {"reranker_score": item["reranker_score"]} if "reranker_score" in item else {})) for item in output]
                    trace["reranker_used"] = True
                except TimeoutError:
                    trace["fallback_reason"] = "reranker_timeout"
                except Exception as exc:
                    trace["fallback_reason"] = "reranker_error:" + type(exc).__name__
        if pipeline.eligibility is not None:
            allowed = pipeline.eligibility()
            ranked = [item for item in ranked if item["document_id"] in allowed]
        parents = pipeline.context_builder.build(ranked, k)
        results, used = [], 0
        for item in parents:
            if used + len(item["content"]) > self.policy.max_context_chars:
                item = dict(item, content=item["chunk_content"], context_scope="child",
                            page_start=item["matched_page_start"], page_end=item["matched_page_end"])
            if used + len(item["content"]) <= self.policy.max_context_chars:
                results.append(item)
                used += len(item["content"])
        trace.update(generation_id=getattr(pipeline, "generation_id", None), candidate_count=len(ranked),
                     context_chars=used, returned_parents=len(results), elapsed_ms=(perf_counter() - started) * 1000)
        return {"results": results, "trace": trace}
