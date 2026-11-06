"""Query authorization, filtering, bounded execution and typed evidence output."""

from threading import BoundedSemaphore
import os
from time import perf_counter

from app.retrieval.filters import filtered_pipeline
from types import SimpleNamespace
from uuid import uuid4
import hashlib
from app.core.contracts import SearchRequest, SearchResponse
from app.core.exceptions import BusyError, NotPublished
from app.core.serialization import public
from app.models.pool import usage_context


class RetrievalService:
    def __init__(self, bases, sessions, access, keys, audit, concurrency=4):
        self.bases, self.sessions, self.access, self.keys, self.audit = (
            bases,
            sessions,
            access,
            keys,
            audit,
        )
        self.slots = BoundedSemaphore(concurrency)
        # A short bounded wait turns bursts into latency instead of instant 503s.
        # Load test, 8 clients / 4 slots: 75 of 80 requests failed without waiting.
        self.queue_seconds = float(os.getenv("RAG_SEARCH_QUEUE_SECONDS", "10"))

    def search(self, actor, request):
        request = SearchRequest.model_validate(request)
        for identity in request.knowledge_base_ids:
            self.access.authorize(actor, identity)
        if not self.slots.acquire(timeout=self.queue_seconds):
            raise BusyError("Search capacity is busy; retry later")
        try:
            # Count quota only for admitted requests; a 503 must not use it up.
            self.keys.reserve(actor)
        except BaseException:
            self.slots.release()
            raise
        started = perf_counter()
        usage = []
        context = usage_context.set(usage)
        try:
            candidates = []
            traces = []
            versions = []
            budgets, rerankers = [], set()
            skipped = []
            for identity in request.knowledge_base_ids:
                kb = self.bases.kb(identity)
                runtime = self.sessions.get(identity)
                try:
                    pipeline = filtered_pipeline(runtime, request)
                except NotPublished:
                    # One unbuilt base must not fail a multi-base search; say so instead.
                    if len(request.knowledge_base_ids) == 1:
                        raise
                    skipped.append(identity)
                    continue
                supplement = request.supplement or request.mode == "high_recall"
                output = runtime.orchestrator.search(
                    SimpleNamespace(pipeline=pipeline),
                    request.query,
                    request.top_k,
                    supplement=supplement,
                    extra_queries=request.queries,
                    min_score=request.min_score,
                )
                budgets.append(runtime.orchestrator.policy.max_context_tokens)
                rerankers.add(
                    runtime.orchestrator.policy.reranker_model
                    if output["trace"]["reranker_used"]
                    else None
                )
                for rank, item in enumerate(output["results"], 1):
                    candidates.append(
                        dict(
                            item,
                            knowledge_base_id=identity,
                            cross_kb_rank_score=1 / (60 + rank),
                            generation_id=output["trace"]["generation_id"],
                            citation=dict(
                                knowledge_base_id=identity,
                                document_id=item["document_id"],
                                version_id=item.get("version_id"),
                                chunk_id=item["chunk_id"],
                                page_start=item.get("page_start"),
                                page_end=item.get("page_end"),
                            ),
                        )
                    )
                traces.append(
                    dict(
                        knowledge_base_id=identity,
                        routes=pipeline.route_trace,
                        **output["trace"],
                    )
                )
                versions.append(
                    dict(
                        knowledge_base_id=identity,
                        configuration_revision=kb["revision"],
                        generation_id=output["trace"]["generation_id"],
                    )
                )
            if len(skipped) == len(request.knowledge_base_ids):
                raise NotPublished("None of the requested knowledge bases is published")
            # Model/reranker work may outlive a deletion. Recheck the live base
            # and document visibility before assembling a successful response.
            for identity in request.knowledge_base_ids:
                self.access.authorize(actor, identity)
                registry = self.sessions.workspaces.get(identity).registry
                requested = {
                    item["document_id"]
                    for item in candidates
                    if item["knowledge_base_id"] == identity
                }
                allowed = registry.eligible_ids(requested)
                if request.as_of:
                    # Historical lifecycle was checked against the publication;
                    # only permanent purges override that historical visibility.
                    allowed = requested - registry.purged_ids()
                candidates = [
                    item
                    for item in candidates
                    if item["knowledge_base_id"] != identity
                    or item["document_id"] in allowed
                ]
            # One reranker model scored every base: its scores are comparable, so a
            # weak base no longer receives the same share of top slots as a strong one.
            # Otherwise per-base scores have different meanings; keep rank fusion.
            by_reranker = (
                len(request.knowledge_base_ids) > 1
                and len(rerankers) == 1
                and None not in rerankers
            )
            candidates.sort(
                key=lambda x: (
                    -(x["reranker_score"] if by_reranker else x["cross_kb_rank_score"]),
                    x["knowledge_base_id"],
                    x["parent_id"],
                )
            )
            # Each base already fitted its own budget; the response uses the strictest.
            budget, results, used = min(budgets), [], 0
            for item in candidates:
                if len(results) >= request.top_k:
                    break
                if used + item["context_tokens"] <= budget:
                    results.append(item)
                    used += item["context_tokens"]
            output = dict(
                schema_version=1,
                request_id=uuid4().hex,
                query=request.query,
                results=public(results),
                metadata=dict(
                    snapshots=versions,
                    elapsed_ms=(perf_counter() - started) * 1000,
                    model_usage=usage,
                    warnings=[
                        t["fallback_reason"] for t in traces if t.get("fallback_reason")
                    ]
                    + [f"not_published:{identity}" for identity in skipped],
                ),
            )
            if request.include_trace:
                output["trace"] = public(traces)
            output = SearchResponse.model_validate(output).model_dump(
                exclude_unset=True
            )
            self.audit.audit(
                actor["id"],
                "search",
                query_hash=hashlib.sha256(request.query.encode()).hexdigest(),
                knowledge_base_ids=request.knowledge_base_ids,
                result_count=len(results),
                elapsed_ms=output["metadata"]["elapsed_ms"],
                usage=usage,
            )
            return output
        except Exception as exc:
            self.audit.audit(
                actor["id"],
                "search_failed",
                query_hash=hashlib.sha256(request.query.encode()).hexdigest(),
                knowledge_base_ids=request.knowledge_base_ids,
                error_type=type(exc).__name__,
                usage=usage,
            )
            raise
        finally:
            usage_context.reset(context)
            self.slots.release()
