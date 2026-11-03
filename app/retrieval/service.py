from threading import BoundedSemaphore
from app.retrieval.filters import filtered_pipeline

"""Query authorization, filtering, bounded execution and typed evidence output."""
from time import perf_counter
from types import SimpleNamespace
from uuid import uuid4
import hashlib
from app.core.contracts import SearchRequest, SearchResponse
from app.core.exceptions import BusyError
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

    def search(self, actor, request):
        request = SearchRequest.model_validate(request)
        for identity in request.knowledge_base_ids:
            self.access.authorize(actor, identity)
        self.keys.reserve(actor)
        if not self.slots.acquire(blocking=False):
            raise BusyError("Search capacity is busy; retry later")
        started = perf_counter()
        usage = []
        context = usage_context.set(usage)
        try:
            candidates = []
            traces = []
            versions = []
            for identity in request.knowledge_base_ids:
                kb = self.bases.kb(identity)
                runtime = self.sessions.get(identity)
                pipeline = filtered_pipeline(runtime, request)
                supplement = request.supplement or request.mode == "high_recall"
                output = runtime.orchestrator.search(
                    SimpleNamespace(pipeline=pipeline),
                    request.query,
                    request.top_k,
                    supplement=supplement,
                )
                for rank, item in enumerate(output["results"], 1):
                    if not kb["profile"].get("parent_context", True):
                        item = dict(
                            item,
                            content=item["chunk_content"],
                            context_scope="child",
                            page_start=item.get("matched_page_start"),
                            page_end=item.get("matched_page_end"),
                        )
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
            candidates.sort(
                key=lambda x: (
                    -x["cross_kb_rank_score"],
                    x["knowledge_base_id"],
                    x["parent_id"],
                )
            )
            results = []
            size = 0
            for item in candidates:
                if len(results) >= request.top_k:
                    break
                if size + len(item["content"]) <= 24000:
                    results.append(item)
                    size += len(item["content"])
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
                    ],
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
