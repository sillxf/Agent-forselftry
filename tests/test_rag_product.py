"""Product acceptance: isolation, publication, migration and bounded adapters. No paid models."""

import hashlib, json, shutil
from pathlib import Path
from uuid import uuid4
import httpx, numpy as np, pytest
from fastapi.testclient import TestClient
from filelock import FileLock, Timeout
from rag_service.api import create_app
from rag_service.catalog import Catalog
from rag_service.contracts import (
    JobRequest,
    KnowledgeBaseCreate,
    ModelConfig,
    SearchRequest,
)
from rag_service.providers import Providers, EmbeddingProvider, ModelPool, usage_context
from rag_service.service import RAGService, AccessDenied
from rag_service.worker import Worker
from rag_service.core.models import ContentBlock, DocumentRecord, ParsedDocument
from rag_service.core.ingestion.docling_parser import file_checksum
from rag_service.maintenance import (
    backup_service,
    restore_service,
    migrate_legacy,
    verify_backup,
)

TOKEN = "product-test-admin-token-1234567890"
ADMIN = {"id": "admin", "admin": True, "scopes": None}


class Tokenizer:
    def encode(self, text, add_special_tokens=False):
        return list(text)

    def num_special_tokens_to_add(self, pair=False):
        return 0


class FakeEmbedding:
    def __init__(self, config):
        self.config = config
        self.calls = []

    def tokenizer_and_limit(self):
        return Tokenizer(), 8192

    def embed_documents(self, texts):
        self.calls.append(("documents", texts))
        return self.encode(texts)

    def embed_query(self, texts):
        self.calls.append(("query", texts))
        return self.encode(texts)

    def encode(self, texts):
        result = np.zeros(
            (len(texts), self.config.get("dimension") or 32), dtype="float32"
        )
        for i, text in enumerate(texts):
            for word in text.lower().split():
                result[
                    i,
                    int(hashlib.sha256(word.encode()).hexdigest()[:8], 16)
                    % result.shape[1],
                ] += 1
        return result


class Parser:
    ocr_enabled = False

    def parse(self, path, source_name=None):
        path = Path(path)
        text = path.read_text(encoding="utf-8")
        checksum = file_checksum(path)
        return ParsedDocument(
            document=DocumentRecord(
                filename=source_name or path.name,
                file_type="md",
                source_path=str(path),
                checksum=checksum,
            ),
            blocks=[
                ContentBlock(
                    document_id=checksum,
                    block_type="paragraph",
                    text=text,
                    page_number=1,
                )
            ],
            markdown=text,
        )


@pytest.fixture
def product(tmp_path):
    root = tmp_path / "service"
    providers = Providers(
        Catalog(root),
        embedding_factory=FakeEmbedding,
        reranker_factory=lambda config: type(
            "Ranker",
            (),
            {
                "rerank": lambda self, q, rows: [
                    dict(x, reranker_score=float(len(rows) - i))
                    for i, x in enumerate(rows)
                ]
            },
        )(),
    )
    service = RAGService(root, admin_token=TOKEN, providers=providers)
    for name in ["Operations", "Development"]:
        service.catalog.create_kb({"name": name, "build": {"ocr_enabled": False}})
    original = service.runtime

    def runtime(*args, **kwargs):
        r = original(*args, **kwargs)
        r.parser = Parser()
        return r

    service.runtime = runtime
    return service


def client(product):
    return TestClient(
        create_app(product),
        base_url="http://127.0.0.1",
        headers={"Authorization": "Bearer " + TOKEN},
    )


def ids(service):
    return [x["id"] for x in service.catalog.list_kbs()]


def upload(c, kb, text="incident failed login mitigation", document_id=None):
    url = f"/api/v1/knowledge-bases/{kb}/documents?filename=manual.md" + (
        f"&document_id={document_id}" if document_id else ""
    )
    r = c.post(url, content=text.encode())
    assert r.status_code == 201, r.text
    return r.json()["document"]["document_id"]


def build(service, c, kb):
    response = c.post(f"/api/v1/knowledge-bases/{kb}/jobs", json={"operation": "build"})
    assert response.status_code == 202, response.text
    Worker(service).run_once()
    job = service.catalog.job(response.json()["id"])
    assert job["status"] == "succeeded", job
    return service.runtime(kb).repository.current_pointer()


def search(c, kbs, **options):
    return c.post(
        "/api/v1/search",
        json={"query": "incident login", "knowledge_base_ids": kbs, **options},
    )


def test_authentication_scopes_host_origin_and_key_redaction(product):
    a, b = ids(product)
    with client(product) as c:
        assert (
            c.get("/api/v1/knowledge-bases", headers={"Authorization": ""}).status_code
            == 401
        )
        assert (
            c.get("/api/v1/me", headers={"Host": "attacker.example"}).status_code == 403
        )
        assert (
            c.post(
                "/api/v1/knowledge-bases",
                json={"name": "bad"},
                headers={"Origin": "https://attacker.example"},
            ).status_code
            == 403
        )
        key = c.post(
            "/api/v1/keys", json={"name": "agent", "knowledge_base_ids": [a]}
        ).json()
        headers = {"Authorization": "Bearer " + key["token"]}
        assert [
            x["id"] for x in c.get("/api/v1/knowledge-bases", headers=headers).json()
        ] == [a]
        assert (
            c.get(f"/api/v1/knowledge-bases/{b}/documents", headers=headers).status_code
            == 403
        )
        assert (
            c.get(
                f"/api/v1/knowledge-bases/{b}/chunks/{uuid4()}", headers=headers
            ).status_code
            == 403
        )
        assert (
            c.post(
                f"/api/v1/knowledge-bases/{a}/jobs",
                json={"operation": "build"},
                headers=headers,
            ).status_code
            == 403
        )
        assert (
            search(c, [a, b], **{}).status_code == 409
        )  # Admin: authorized but no published snapshot.
        assert (
            c.post(
                "/api/v1/search",
                json={"query": "x", "knowledge_base_ids": [b]},
                headers=headers,
            ).status_code
            == 403
        )
        assert key["token"] not in c.get("/api/v1/keys").text
        assert "digest" not in c.get("/api/v1/keys").text
        c.delete("/api/v1/keys/" + key["id"])
        assert c.get("/api/v1/me", headers=headers).status_code == 401


def test_upload_build_versions_trace_filters_and_explicit_supplement(product):
    a, b = ids(product)
    with client(product) as c:
        doc = upload(c, a)
        other = upload(c, a, "software deployment rollback pipeline")
        assert search(c, [a]).status_code == 409
        c.patch(
            f"/api/v1/knowledge-bases/{a}/documents/{doc}",
            json={"metadata": {"domain": "security"}},
        )
        first = build(product, c, a)
        result = search(c, [a], include_trace=True, supplement=True).json()
        assert result["results"] and result["metadata"]["warnings"] == [
            "multi_view_disabled"
        ]
        assert {x["stage"] for x in result["trace"][0]["routes"]} == {"dense", "sparse"}
        assert str(product.root) not in json.dumps(result)
        filtered = search(c, [a], filters={"metadata.domain": "security"}).json()
        assert {r["document_id"] for r in filtered["results"]} == {doc}
        assert search(c, [a], filters={"arbitrary": "bad"}).status_code == 409
        detail = c.get(f"/api/v1/knowledge-bases/{a}/documents/{doc}").json()
        assert (
            detail["children"] and detail["markdown"] is None
        )  # The fake parser does not archive Markdown.
        child = detail["children"][0]
        assert (
            c.get(f"/api/v1/knowledge-bases/{a}/chunks/{child['chunk_id']}").status_code
            == 200
        )
        assert c.get(
            f"/api/v1/knowledge-bases/{b}/chunks/{child['chunk_id']}"
        ).status_code in {404, 409}
        upload(c, a, "updated incident login recommendations", doc)
        assert (
            len(
                next(d for d in product.documents(ADMIN, a) if d["document_id"] == doc)[
                    "versions"
                ]
            )
            == 2
        )
        assert (
            search(c, [a]).json()["results"][0]["generation_id"] == first["generation"]
        )
        second = build(product, c, a)
        assert second["generation"] != first["generation"]
        historical = search(c, [a], as_of=first["published_at"]).json()
        assert (
            historical["metadata"]["snapshots"][0]["generation_id"]
            == first["generation"]
        )
        assert search(c, [a], as_of="2000-01-01T00:00:00Z").status_code == 409
        assert (
            str(product.root)
            not in c.get(f"/api/v1/knowledge-bases/{a}/documents").text
        )


def test_atomic_model_change_and_configuration_optimism(product):
    a, _ = ids(product)
    with client(product) as c:
        upload(c, a)
        first = build(product, c, a)
        old = product.catalog.kb(a)
        model = c.post(
            "/api/v1/models",
            json={
                "kind": "embedding",
                "provider": "sentence_transformers",
                "model": "fake-new-space",
                "dimension": 48,
            },
        ).json()
        body = {k: old[k] for k in ["name", "description", "build", "profile"]}
        body["build"] = dict(body["build"], embedding_id=model["id"])
        assert (
            c.put(
                f"/api/v1/knowledge-bases/{a}?revision={old['revision']}", json=body
            ).status_code
            == 200
        )
        assert (
            c.put(
                f"/api/v1/knowledge-bases/{a}?revision={old['revision']}", json=body
            ).status_code
            == 409
        )
        assert (
            search(c, [a]).json()["metadata"]["snapshots"][0]["generation_id"]
            == first["generation"]
        )
        assert product.status(ADMIN, a)["configuration_pending"] is True
        second = build(product, c, a)
        assert product.runtime(a).pipeline.dense.store.dimension == 48
        assert product.status(ADMIN, a)["configuration_pending"] is False
        rollback = c.post(
            f"/api/v1/knowledge-bases/{a}/jobs",
            json={"operation": "rollback", "generation_id": first["generation"]},
        )
        Worker(product).run_once()
        assert product.catalog.job(rollback.json()["id"])["status"] == "succeeded"
        assert search(c, [a]).status_code == 200
        assert product.runtime(a).pipeline.dense.store.dimension == 32
        assert product.status(ADMIN, a)["configuration_pending"] is True
        c.put(f"/api/v1/models/{model['id']}/enabled", json={"enabled": False})
        assert (
            c.post(
                f"/api/v1/knowledge-bases/{a}/jobs", json={"operation": "build"}
            ).status_code
            == 409
        )


def test_stale_queued_build_never_publishes_and_job_idempotency(product):
    a, _ = ids(product)
    with client(product) as c:
        upload(c, a)
        first = build(product, c, a)
        request = {"operation": "build"}
        headers = {"Idempotency-Key": "same-request-123"}
        one = c.post(
            f"/api/v1/knowledge-bases/{a}/jobs", json=request, headers=headers
        ).json()
        two = c.post(
            f"/api/v1/knowledge-bases/{a}/jobs", json=request, headers=headers
        ).json()
        assert one["id"] == two["id"]
        old = product.catalog.kb(a)
        body = {k: old[k] for k in ["name", "description", "build", "profile"]}
        body["build"] = dict(body["build"], child_tokens=300)
        product.catalog.configure(a, body, old["revision"])
        Worker(product).run_once()
        assert product.catalog.job(one["id"])["status"] == "failed"
        assert (
            product.runtime(a).repository.current_pointer()["generation"]
            == first["generation"]
        )
        assert c.post("/api/v1/jobs/" + one["id"] + "/retry").status_code == 202
        Worker(product).run_once()
        assert (
            product.runtime(a).repository.current_pointer()["generation"]
            != first["generation"]
        )


def test_delete_restore_purge_and_history_access(product):
    a, _ = ids(product)
    with client(product) as c:
        doc = upload(c, a)
        first = build(product, c, a)
        c.delete(f"/api/v1/knowledge-bases/{a}/documents/{doc}")
        assert search(c, [a]).json()["results"] == []
        c.post(f"/api/v1/knowledge-bases/{a}/documents/{doc}/undelete")
        assert search(c, [a]).json()["results"]
        assert (
            c.post(
                f"/api/v1/knowledge-bases/{a}/jobs",
                json={"operation": "purge", "document_id": doc},
            ).status_code
            == 422
        )
        purge = c.post(
            f"/api/v1/knowledge-bases/{a}/jobs",
            json={"operation": "purge", "document_id": doc, "confirm": True},
        )
        Worker(product).run_once()
        assert product.catalog.job(purge.json()["id"])["status"] == "succeeded"
        assert search(c, [a]).json()["results"] == []
        assert search(c, [a], as_of=first["published_at"]).status_code == 409
        assert c.get(f"/api/v1/knowledge-bases/{a}/documents/{doc}").status_code == 404
        assert product.documents(ADMIN, a)[0]["purge_state"] == "completed"


def test_rate_limits_no_query_logging_and_request_bounds(product, monkeypatch):
    a, _ = ids(product)
    with client(product) as c:
        doc = upload(c, a)
        build(product, c, a)
        key = c.post(
            "/api/v1/keys",
            json={
                "name": "limited",
                "knowledge_base_ids": [a],
                "requests_per_minute": 1,
            },
        ).json()
        headers = {"Authorization": "Bearer " + key["token"]}
        body = {"query": "private secret question", "knowledge_base_ids": [a]}
        assert c.post("/api/v1/search", json=body, headers=headers).status_code == 200
        assert c.post("/api/v1/search", json=body, headers=headers).status_code == 429
        assert "private secret question" not in c.get("/api/v1/audit").text
        assert c.post("/api/v1/search", content=b"x" * 65537).status_code == 413
        monkeypatch.setenv("RAG_UPLOAD_MAX_BYTES", "5")
        assert (
            c.post(
                f"/api/v1/knowledge-bases/{a}/documents?filename=x.md",
                content=b"123456",
            ).status_code
            == 413
        )
        assert not list(product.runtime(a).knowledge_dir.glob("*.upload"))
        assert (
            c.post(
                f"/api/v1/knowledge-bases/{a}/documents?filename=../x.md", content=b"x"
            ).status_code
            == 409
        )


def test_worker_interruption_not_silently_replayed(product):
    a, _ = ids(product)
    job = product.submit(ADMIN, a, JobRequest())
    product.catalog.claim()
    product.catalog.recover()
    assert product.catalog.job(job["id"])["status"] == "interrupted"
    assert Worker(product).run_once() is False


def test_remote_provider_usage_and_dimension_validation_without_network():
    seen = []

    def handle(request):
        seen.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "data": [{"index": 0, "embedding": [1, 2, 3]}],
                "usage": {"total_tokens": 2},
            },
        )

    config = ModelConfig(
        kind="embedding",
        provider="openai_compatible",
        model="remote",
        dimension=3,
        tokenizer="local-tokenizer",
        base_url="https://example.invalid/v1",
    )
    provider = EmbeddingProvider(
        config, ModelPool(), transport=httpx.MockTransport(handle)
    )
    usage = []
    token = usage_context.set(usage)
    try:
        assert provider.embed_query(["test"]).shape == (1, 3)
    finally:
        usage_context.reset(token)
    assert (
        usage[0]["reported_usage"]["total_tokens"] == 2
        and seen[0]["encoding_format"] == "float"
    )
    bad = EmbeddingProvider(
        config.model_copy(update={"dimension": 4}),
        ModelPool(),
        transport=httpx.MockTransport(handle),
    )
    with pytest.raises(ValueError, match="dimension"):
        bad.embed_query(["test"])


def test_offline_backup_restore_preserves_ids_paths_and_refuses_live_writers(
    product, tmp_path
):
    a, _ = ids(product)
    with client(product) as c:
        doc = upload(c, a)
        pointer = build(product, c, a)
        with pytest.raises(Timeout):
            backup_service(product.root, tmp_path / "live-backup")
    backup = tmp_path / "backup"
    backup_service(product.root, backup)
    verify_backup(backup)
    restored = tmp_path / "restored"
    restore_service(backup, restored)
    with pytest.raises(ValueError):
        restore_service(backup, restored)
    record = Catalog(restored).kb(a)
    assert record["id"] == a
    from rag_service.core.lifecycle.registry import DocumentRegistry

    registry = DocumentRegistry(restored / "bases" / a / "storage")
    d = registry.get_document(doc)
    assert Path(d.source_path).is_relative_to(restored)
    assert Path(registry.list_versions(doc)[0].source_blob_path).is_relative_to(
        restored
    )
    from rag_service.core.indexing.snapshot_repository import SnapshotRepository

    repository = SnapshotRepository(restored / "bases" / a / "storage")
    assert repository.current_pointer()["generation"] == pointer["generation"]
    repository.load_generation(pointer["generation"])
    (backup / "snapshot/catalog.sqlite3").write_bytes(b"corrupted")
    with pytest.raises(ValueError, match="checksum"):
        verify_backup(backup)


def test_legacy_migration_retains_versions_and_retires_old_writer(product, tmp_path):
    from rag_service.core.retriever import KnowledgeRetriever

    knowledge = tmp_path / "legacy/knowledge"
    knowledge.mkdir(parents=True)
    (knowledge / "runbook.md").write_text(
        "incident login remediation", encoding="utf-8"
    )
    storage = tmp_path / "legacy/storage"
    old = KnowledgeRetriever(
        build=False,
        auto_build=False,
        knowledge_dir=knowledge,
        storage_dir=storage,
        parser=Parser(),
        tokenizer=Tokenizer(),
        embedding_fn=FakeEmbedding({}).embed_documents,
        model_name="legacy-model",
    )
    old.build_index()
    document = old.registry.list_documents()[0]
    pointer = old.repository.current_pointer()
    with pytest.raises(ValueError):
        migrate_legacy(product, knowledge, storage, tmp_path / "backup")
    result = migrate_legacy(
        product, knowledge, storage, tmp_path / "backup", writers_stopped=True
    )
    new = product.runtime(result["knowledge_base_id"])
    assert new.registry.list_documents()[0].document_id == document.document_id
    assert new.repository.current_pointer()["generation"] == pointer["generation"]
    assert product.search(
        ADMIN,
        {"query": "incident", "knowledge_base_ids": [result["knowledge_base_id"]]},
    )["results"]
    assert Path(
        new.registry.list_versions(document.document_id)[0].source_blob_path
    ).is_relative_to(product.root)
    with pytest.raises(ValueError, match="retired"):
        old.build_index()


def test_mcp_http_and_rest_share_authorization_and_evidence(product):
    a, b = ids(product)
    with client(product) as c:
        upload(c, a)
        build(product, c, a)
        headers = {"Accept": "application/json, text/event-stream"}
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "acceptance", "version": "1"},
            },
        }
        r = c.post("/mcp/", json=request, headers=headers)
        assert r.status_code == 200, r.text
        tools = c.post(
            "/mcp/",
            json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            headers=headers,
        ).json()
        assert len(tools["result"]["tools"]) == 6
        key = c.post(
            "/api/v1/keys", json={"name": "mcp-agent", "knowledge_base_ids": [a]}
        ).json()
        headers["Authorization"] = "Bearer " + key["token"]
        r = c.post(
            "/mcp/",
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "rag_search",
                    "arguments": {"query": "incident", "knowledge_base_ids": [a]},
                },
            },
            headers=headers,
        )
        assert r.status_code == 200, r.text
        data = r.json()["result"]
        assert not data.get("isError"), data
        assert data["structuredContent"]["results"]
        r = c.post(
            "/mcp/",
            json={
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "rag_list_documents",
                    "arguments": {"knowledge_base_id": b},
                },
            },
            headers=headers,
        )
        assert r.json()["result"]["isError"] is True


def test_cross_platform_path_rebase_never_edits_source_text(tmp_path):
    from rag_service.maintenance import relocate_storage

    storage = tmp_path / "storage"
    (storage / "parsed").mkdir(parents=True)
    old = "C:\\old\\rag-data"
    target = tmp_path / "new-data"
    path = storage / "parsed/metadata.json"
    path.write_text(
        json.dumps(
            {
                "source_path": old + "\\bases\\abc\\knowledge\\file.md",
                "content": old + "\\unchanged evidence",
                "table_data": [{"path": old + "\\source evidence"}],
            }
        ),
        encoding="utf-8",
    )
    relocate_storage(storage, [(old, target)])
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["source_path"] == str(target / "bases/abc/knowledge/file.md")
    assert data["content"] == old + "\\unchanged evidence"
    assert data["table_data"] == [{"path": old + "\\source evidence"}]


def test_failed_remote_attempt_is_counted_and_preflight_budget_blocks_calls(
    monkeypatch,
):
    seen = []

    def handle(request):
        seen.append(request)
        return httpx.Response(503)

    config = ModelConfig(
        kind="embedding",
        provider="openai_compatible",
        model="remote",
        dimension=3,
        tokenizer="local-tokenizer",
        base_url="https://example.invalid/v1",
    )
    provider = EmbeddingProvider(
        config, ModelPool(), transport=httpx.MockTransport(handle)
    )
    usage = []
    token = usage_context.set(usage)
    try:
        with pytest.raises(httpx.HTTPStatusError):
            provider.embed_query(["test"])
        assert (
            len(usage) == 1
            and usage[0]["requests"] == 1
            and usage[0]["reported_usage"] is None
        )
        monkeypatch.setenv("RAG_REMOTE_MAX_REQUESTS_PER_OPERATION", "1")
        with pytest.raises(ValueError, match="budget"):
            provider.embed_query(["test"])
        assert len(seen) == 1
    finally:
        usage_context.reset(token)


def test_readers_cannot_fetch_unpublished_generation(product):
    a, _ = ids(product)
    with client(product) as c:
        document = upload(c, a)
        build(product, c, a)
        runtime = product.runtime(a)
        snapshot, pointer = runtime.repository.load_published()
        orphan = runtime.repository.save(snapshot, pointer["signature"])
        assert (runtime.repository.root / orphan.generation).exists()
        assert (
            c.get(
                f"/api/v1/knowledge-bases/{a}/documents/{document}?generation_id={orphan.generation}"
            ).status_code
            == 404
        )
        chunk = snapshot.store.records[0]["chunk_id"]
        assert (
            c.get(
                f"/api/v1/knowledge-bases/{a}/chunks/{chunk}?generation_id={orphan.generation}"
            ).status_code
            == 404
        )
