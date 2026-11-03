"""Transport-independent application services used by REST, MCP and the worker."""

from collections import OrderedDict
from copy import copy
from pathlib import Path
from threading import BoundedSemaphore, RLock
from time import perf_counter
from types import SimpleNamespace
from uuid import uuid4
import hashlib, hmac, json, os, re
from rag_service.catalog import Catalog
from rag_service.contracts import (
    IndexBuildConfig,
    RetrievalProfile,
    SearchRequest,
    SearchResponse,
)
from rag_service.core.retriever import KnowledgeRetriever
from rag_service.core.ingestion.docling_parser import DoclingParser
from rag_service.core.lifecycle.versions import HistoricalRetriever
from rag_service.providers import Providers, usage_context


class AccessDenied(PermissionError):
    pass


class BusyError(RuntimeError):
    pass


def public(value):
    """Never disclose local filesystem topology through evidence or management APIs."""
    hidden = {
        "source_path",
        "source_blob_path",
        "image_path",
        "image_paths",
        "path",
        "path_key",
        "source_key",
    }
    if isinstance(value, dict):
        return {
            k: (v if k in {"table_data", "metadata"} else public(v))
            for k, v in value.items()
            if k not in hidden
        }
    if isinstance(value, list):
        return [public(v) for v in value]
    return value


class RAGService:
    def __init__(self, root, *, admin_token=None, providers=None, runtime_factory=None):
        self.catalog = Catalog(root)
        self.root = self.catalog.root
        token_file = self.root / "admin.token"
        self.admin_token = (
            admin_token
            or os.getenv("RAG_SERVICE_ADMIN_TOKEN")
            or (token_file.read_text().strip() if token_file.exists() else "")
        )
        if len(self.admin_token) < 24:
            raise ValueError(
                "Run rag-service init or set RAG_SERVICE_ADMIN_TOKEN (at least 24 characters)"
            )
        self.providers = providers or Providers(self.catalog)
        self.runtime_factory = runtime_factory
        self.runtimes = OrderedDict()
        self.lock = RLock()
        self.search_slots = BoundedSemaphore(
            int(os.getenv("RAG_SEARCH_CONCURRENCY", "4"))
        )
        from rag_service.core.config import RAG_EMBEDDING_MODEL, RAG_RERANKER_MODEL

        for identity, config in [
            (
                "default-embedding",
                dict(
                    kind="embedding",
                    provider="sentence_transformers",
                    model=RAG_EMBEDDING_MODEL,
                ),
            ),
            (
                "default-reranker",
                dict(
                    kind="reranker", provider="cross_encoder", model=RAG_RERANKER_MODEL
                ),
            ),
        ]:
            try:
                self.catalog.model(identity)
            except KeyError:
                self.catalog.add_model(config, identity=identity)

    def authenticate(self, token):
        if token and hmac.compare_digest(token, self.admin_token):
            return dict(id="admin", admin=True, scopes=None)
        actor = self.catalog.authenticate(token)
        if actor is None:
            raise AccessDenied("Valid service credentials required")
        return actor

    def authorize(self, actor, kb_id=None, *, admin=False):
        if admin and not actor["admin"]:
            raise AccessDenied("Administrator permission required")
        if kb_id is not None:
            if not actor["admin"] and kb_id not in actor["scopes"]:
                raise AccessDenied("Knowledge base access denied")
            return self.catalog.kb(kb_id)

    def list_kbs(self, actor):
        return [
            k
            for k in self.catalog.list_kbs()
            if actor["admin"] or k["id"] in actor["scopes"]
        ]

    def validate_config(self, body):
        embedding = self.catalog.model(body.build.embedding_id, require_enabled=True)
        reranker = self.catalog.model(body.profile.reranker_id, require_enabled=True)
        if (
            embedding["config"]["kind"] != "embedding"
            or reranker["config"]["kind"] != "reranker"
        ):
            raise ValueError("Incorrect model role")

    def runtime(self, kb_id, *, configuration=None):
        kb = configuration or self.catalog.kb(kb_id)
        key = (
            kb_id,
            json.dumps(
                {"build": kb["build"], "profile": kb["profile"]}, sort_keys=True
            ),
        )
        with self.lock:
            if key not in self.runtimes:
                base = self.root / "bases" / kb_id
                (base / "knowledge").mkdir(parents=True, exist_ok=True)
                if self.runtime_factory:
                    runtime = self.runtime_factory(base, kb)
                else:
                    build = IndexBuildConfig.model_validate(kb["build"])
                    parser = DoclingParser(
                        archive_dir=base / "storage/parsed",
                        image_dir=base / "storage/images",
                        ocr_enabled=build.ocr_enabled,
                    )
                    profile = RetrievalProfile.model_validate(kb["profile"]).model_copy(
                        update={
                            "reranker_model": "provider:" + kb["profile"]["reranker_id"]
                        }
                    )
                    runtime = KnowledgeRetriever(
                        build=False,
                        auto_build=False,
                        knowledge_dir=base / "knowledge",
                        storage_dir=base / "storage",
                        parser=parser,
                        model_name="provider:" + build.embedding_id,
                        embedding_resolver=self.providers.embedding,
                        parent_max_tokens=build.parent_tokens,
                        child_max_tokens=build.child_tokens,
                        overlap_tokens=build.overlap_tokens,
                        retrieval_policy=profile,
                        reranker_factory=lambda: self.providers.reranker(
                            "provider:" + profile.reranker_id
                        ),
                    )
                self.runtimes[key] = runtime
                while len(self.runtimes) > 8:
                    self.runtimes.popitem(last=False)
            self.runtimes.move_to_end(key)
            return self.runtimes[key]

    def status(self, actor, kb_id):
        kb = self.authorize(actor, kb_id)
        r = self.runtime(kb_id)
        pointer = r.repository.current_pointer()
        manifest = (
            r.repository._read_manifest(pointer["generation"]) if pointer else None
        )
        active = pointer["signature"]["model"] if pointer else None
        desired = "provider:" + kb["build"]["embedding_id"]
        # Compare the entire desired build identity, not merely model names.
        sig = pointer.get("signature", {}) if pointer else {}
        build = kb["build"]
        needs_build = (
            not pointer
            or active != desired
            or any(
                sig.get(k) != build[v]
                for k, v in [
                    ("parent_tokens", "parent_tokens"),
                    ("child_tokens", "child_tokens"),
                    ("overlap", "overlap_tokens"),
                    ("ocr", "ocr_enabled"),
                ]
            )
        )
        return public(
            dict(
                knowledge_base=kb,
                current=pointer,
                counts=manifest["counts"] if manifest else {},
                active_embedding=active,
                desired_embedding=desired,
                configuration_pending=needs_build,
                core_jobs=r.registry.list_jobs(),
                jobs=self.catalog.jobs(kb_id),
            )
        )

    def _filtered_pipeline(self, runtime, request):
        if request.as_of:
            snapshot, publication = runtime.repository.at(request.as_of)
            source = HistoricalRetriever(
                runtime, snapshot, publication, request.as_of
            ).pipeline
        else:
            source = runtime.pipeline
        pipeline = copy(source)
        pipeline.route_trace = []
        original = source.eligibility
        filters = request.filters
        if any(
            not (
                k in {"document_id", "file_type"}
                or re.fullmatch(r"metadata\.[\w-]{1,80}", k)
            )
            for k in filters
        ):
            raise ValueError("Unsupported metadata filter")
        if any(
            len(v if isinstance(v, list) else [v]) > 50
            or any(len(x) > 1000 for x in (v if isinstance(v, list) else [v]))
            for v in filters.values()
        ):
            raise ValueError("Metadata filter is too large")

        def eligible():
            ids = (
                original()
                if original
                else {x["document_id"] for x in source.dense.store.records}
            )
            if not filters:
                return ids
            docs = {d.document_id: d for d in runtime.registry.list_documents()}
            types = {
                x["document_id"]: x.get("file_type", "")
                for x in source.dense.store.records
            }

            def match(identity):
                document = docs[identity]
                for field, expected in filters.items():
                    actual = (
                        identity
                        if field == "document_id"
                        else types.get(identity)
                        if field == "file_type"
                        else document.metadata.get(field.removeprefix("metadata."))
                    )
                    if actual not in (
                        expected if isinstance(expected, list) else [expected]
                    ):
                        return False
                return True

            return {i for i in ids if i in docs and match(i)}

        pipeline.eligibility = eligible
        return pipeline

    def search(self, actor, request):
        request = SearchRequest.model_validate(request)
        for identity in request.knowledge_base_ids:
            self.authorize(actor, identity)
        self.catalog.reserve(actor)
        if not self.search_slots.acquire(blocking=False):
            raise BusyError("Search capacity is busy; retry later")
        started = perf_counter()
        usage = []
        context = usage_context.set(usage)
        try:
            candidates = []
            traces = []
            versions = []
            for identity in request.knowledge_base_ids:
                kb = self.catalog.kb(identity)
                runtime = self.runtime(identity)
                pipeline = self._filtered_pipeline(runtime, request)
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
            self.catalog.audit(
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
            self.catalog.audit(
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
            self.search_slots.release()

    def documents(self, actor, kb_id):
        self.authorize(actor, kb_id)
        r = self.runtime(kb_id)
        pointer = r.repository.current_pointer()
        manifest = r.repository._read_manifest(pointer["generation"]) if pointer else {}
        published = {x["document_id"]: x for x in (manifest or {}).get("documents", [])}
        output = []
        for d in r.registry.list_documents():
            state = (
                "purged"
                if d.purged_at
                else "deleted"
                if d.deleted_at
                else "published"
                if d.document_id in published
                else "uploaded"
            )
            purge_state = None
            if d.purged_at:
                path = r.storage_dir / "purges" / (d.document_id + ".json")
                purge_state = (
                    json.loads(path.read_text())["status"]
                    if path.exists()
                    else "plan_unavailable"
                )
                if purge_state != "completed":
                    state = "purge_incomplete"
            versions = r.registry.list_versions(d.document_id)
            served = published.get(d.document_id)
            output.append(
                public(
                    dict(
                        **d.model_dump(),
                        name=Path(d.source_path).name,
                        file_type=versions[-1].file_type if versions else "",
                        status=state,
                        purge_state=purge_state,
                        published=served,
                        needs_build=not d.purged_at
                        and (
                            not served
                            or served.get("version_id")
                            != (d.selected_version_id or d.latest_version_id)
                        ),
                        versions=[v.model_dump() for v in versions],
                        view_states=r.registry.view_states(d.document_id),
                        view_count=sum(
                            v["count"]
                            for v in (manifest or {}).get("view_assets", [])
                            if v["document_id"] == d.document_id
                        ),
                    )
                )
            )
        return output

    def document(
        self, actor, kb_id, document_id, *, generation_id=None, offset=0, limit=50
    ):
        self.authorize(actor, kb_id)
        r = self.runtime(kb_id)
        d = r.registry.get_document(document_id)
        if d.purged_at or d.deleted_at:
            raise KeyError("Document unavailable")
        pointer = r.repository.current_pointer()
        if generation_id and generation_id not in {
            p["generation"] for p in r.repository.publications() if p["available"]
        }:
            raise KeyError("Generation was never published or is unavailable")
        snapshot = (
            r.repository.load_generation(generation_id)
            if generation_id
            else r.repository.load_generation(pointer["generation"])
            if pointer
            else None
        )
        record = (
            next((x for x in snapshot.documents if x.document_id == document_id), None)
            if snapshot
            else None
        )
        parents = (
            [
                p.model_dump(mode="json")
                for p in snapshot.parents
                if p.document_id == document_id
            ]
            if snapshot
            else []
        )
        children = (
            [c for c in snapshot.store.records if c["document_id"] == document_id]
            if snapshot
            else []
        )
        ids = {c["chunk_id"] for c in children}
        views = (
            [v for v in snapshot.view_store.records if v["source_child_id"] in ids]
            if snapshot and snapshot.view_store
            else []
        )
        markdown = None
        if record:
            path = r.storage_dir / "parsed" / (record.checksum + ".md")
            if path.exists():
                markdown = path.read_text(encoding="utf-8")
        return public(
            dict(
                document=d.model_dump(),
                generation_id=generation_id or (pointer or {}).get("generation"),
                published=record.model_dump(mode="json") if record else None,
                markdown=markdown[:200000] if markdown else markdown,
                markdown_truncated=bool(markdown and len(markdown) > 200000),
                pagination={
                    "offset": offset,
                    "limit": limit,
                    "parents": len(parents),
                    "children": len(children),
                    "views": len(views),
                },
                parents=parents[offset : offset + limit],
                children=children[offset : offset + limit],
                views=views[offset : offset + limit],
                outline=[
                    {
                        "section_path": p["section_path"],
                        "page_start": p["page_start"],
                        "parent_id": p["parent_id"],
                    }
                    for p in parents[:1000]
                ],
            )
        )

    def chunk(self, actor, kb_id, chunk_id, *, generation_id=None):
        self.authorize(actor, kb_id)
        r = self.runtime(kb_id)
        pointer = r.repository.current_pointer()
        if not pointer and not generation_id:
            raise KeyError("No published index")
        if generation_id and generation_id not in {
            p["generation"] for p in r.repository.publications() if p["available"]
        }:
            raise KeyError("Generation was never published or is unavailable")
        snapshot = r.repository.load_generation(generation_id or pointer["generation"])
        item = next(
            (x for x in snapshot.store.records if x["chunk_id"] == chunk_id), None
        )
        if item is None or item["document_id"] not in r.registry.eligible_ids(
            [item["document_id"]]
        ):
            raise KeyError("Chunk unavailable")
        return public(item)

    def submit(self, actor, kb_id, request, *, idempotency=None):
        kb = self.authorize(actor, kb_id, admin=True)
        if request.operation == "build":
            self.catalog.model(kb["build"]["embedding_id"], require_enabled=True)
        if request.operation == "purge":
            self.runtime(kb_id).registry.get_document(request.document_id)
        payload = dict(request.model_dump(), configuration=kb)
        job = self.catalog.enqueue(kb_id, request.operation, payload, idempotency)
        self.catalog.audit(
            actor["id"],
            "job_submitted",
            kb_id,
            job_id=job["id"],
            operation=request.operation,
        )
        return job
