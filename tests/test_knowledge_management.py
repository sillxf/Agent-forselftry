"""One bounded acceptance batch: lifecycle, incremental indexes, views, caller control and HTTP."""
import json
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from rank_bm25 import BM25Plus

from app.api.knowledge import create_knowledge_router
from app.rag.retrieval.policy import RetrievalPolicy
from app.rag.retrieval.sparse import SparseRetriever, tokenize
from app.rag.view_generation import ViewConfig
from app.rag.views import make_question_view


def write(factory, name="manual.md", text="# Manual\n\nOriginal unique login evidence."):
    source = factory.knowledge / name
    source.write_text(text, encoding="utf-8")
    return source


def test_incremental_updates_vectors_and_sparse_without_touching_current(rag_factory):
    write(rag_factory, "a.md")
    changed = write(rag_factory, "b.md", "# Second\n\nOld obsolete tokens.")
    owner = rag_factory()
    pinned = owner.pipeline
    old_vectors = owner.store.index.reconstruct_n(0, len(owner.store.records)).copy()
    owner.parser.parse = Mock(wraps=owner.parser.parse)
    owner.embedding_fn = Mock(wraps=owner.embedding_fn)
    changed.write_text("# Second\n\nNew replacement tokens.", encoding="utf-8")
    owner.build_index()
    assert owner.last_build_metrics["build_mode"] == "incremental"
    assert owner.last_build_metrics["reused_documents"] == 1
    assert owner.parser.parse.call_count == 1
    assert "obsolete" not in owner.pipeline.sparse.postings
    assert "replacement" in owner.pipeline.sparse.postings
    assert np.array_equal(pinned.dense.store.index.reconstruct_n(0, len(pinned.dense.store.records)), old_vectors)
    assert pinned.sparse.retrieve("obsolete", 5)
    assert not owner.pipeline.sparse.retrieve("obsolete", 5)
    owner.embedding_fn.reset_mock()
    owner.build_index()
    owner.embedding_fn.assert_not_called()
    assert owner.last_build_metrics["retained_chunks"] == len(owner.store.records)


def test_sparse_incremental_formula_matches_independent_bm25plus():
    records = [{"chunk_id":"a", "search_text":"one one two"},{"chunk_id":"b", "search_text":"two three"}]
    sparse = SparseRetriever(records)
    records = [records[0], {"chunk_id":"c", "search_text":"new three three"}]
    updated = sparse.updated(records)
    expected = BM25Plus([tokenize(r["search_text"]) for r in records])
    assert np.allclose(updated.bm25.get_scores(["one","three","missing"]), expected.get_scores(["one","three","missing"]))
    loaded = SparseRetriever(records, payload=updated.payload())
    assert loaded.retrieve("three one", 5) == updated.retrieve("three one", 5)


def test_historical_publications_and_single_document_restore(rag_factory):
    source = write(rag_factory)
    owner = rag_factory()
    document = owner.documents[0]
    first_time = owner.repository.current_pointer()["published_at"]
    source.write_text("# Changed\n\nUpdated evidence only.", encoding="utf-8")
    owner.build_index()
    assert "Original" in owner.search_with_trace("unique", as_of=first_time)["results"][0]["content"]
    owner.restore_version(document.document_id, document.version_id)
    owner.build_index()
    assert owner.documents[0].version_id == document.version_id
    assert "Original" in owner.search("unique", 1)[0]["content"]
    assert "Updated" in source.read_text(encoding="utf-8")  # No external file overwrite.
    owner.lifecycle.delete(document.document_id)
    assert owner.search("unique", 1) == []
    assert owner.search_with_trace("unique", as_of=first_time)["results"]
    owner.lifecycle.restore(document.document_id)
    with pytest.raises(ValueError, match="timezone"):
        owner.search_with_trace("unique", as_of="2026-01-01T00:00:00")
    with pytest.raises(ValueError, match="No retained"):
        owner.search_with_trace("unique", as_of="2000-01-01T00:00:00Z")
    source.write_text("# New source\n\nThird content unpins the selected version.", encoding="utf-8")
    owner.build_index()
    assert owner.registry.get_document(document.document_id).selected_version_id is None


class LocalGenerator:
    model = "test-view-model"
    def __init__(self):
        self.calls = 0
    def chat(self, messages):
        self.calls += 1
        return {"content":json.dumps({"questions":[{"source_index":0,"zh":"登录证据是什么？","en":"What is the login evidence?"}]}),
                "usage":{"prompt_tokens":10,"completion_tokens":5,"total_tokens":15}}


def test_view_opt_in_cache_version_invalidation_and_usage(rag_factory):
    source = write(rag_factory)
    generator = LocalGenerator()
    owner = rag_factory(view_llm_factory=lambda config:generator)
    document_id = owner.documents[0].document_id
    assert generator.calls == 0
    owner.registry.configure(document_id, view_config=ViewConfig(enabled=True, model=generator.model).model_dump())
    owner.build_index()
    assert owner.pipeline.multi_view_dense is not None and generator.calls == 1
    assert owner.last_build_metrics["view_usage"]["total_tokens"] == 15
    first_ids = {r["view_id"] for r in owner.pipeline.multi_view_dense.view_store.records}
    owner.build_index()
    assert generator.calls == 1 and owner.last_build_metrics["view_usage"]["requests"] == 0
    source.write_text("# Changed\n\nOther login evidence.", encoding="utf-8")
    owner.build_index()
    assert generator.calls == 2
    assert first_ids.isdisjoint(r["view_id"] for r in owner.pipeline.multi_view_dense.view_store.records)
    assert any(s["status"] == "stale" for s in owner.registry.view_states(document_id))
    owner.registry.configure(document_id, view_config={"enabled":False})
    owner.build_index()
    assert owner.pipeline.multi_view_dense is None and generator.calls == 2


@pytest.mark.parametrize("failure_policy", ["publish_without_views", "fail_build"])
def test_view_failure_and_preflight_request_budget(rag_factory, monkeypatch, failure_policy):
    write(rag_factory)
    factory = Mock(side_effect=AssertionError("Budget rejection must happen before model construction"))
    owner = rag_factory(view_llm_factory=factory)
    old = owner.repository.current_pointer()["generation"]
    owner.registry.configure(owner.documents[0].document_id, view_config={"enabled":True,"failure_policy":failure_policy})
    monkeypatch.setenv("RAG_VIEW_MAX_REQUESTS_PER_BUILD", "0")
    if failure_policy == "fail_build":
        with pytest.raises(ValueError, match="budget"):
            owner.build_index()
        assert owner.repository.current_pointer()["generation"] == old
    else:
        owner.build_index()
        assert owner.pipeline.multi_view_dense is None
    factory.assert_not_called()
    assert owner.registry.view_states()[0]["status"] == "failed"


def test_only_caller_requests_supplement_and_reranker_failure_keeps_primary(rag_factory):
    write(rag_factory)
    ranker = Mock()
    ranker.rerank.side_effect = lambda query, rows:[dict(r, content="fabricated",reranker_score=1) for r in reversed(rows)]
    owner = rag_factory(retrieval_policy=RetrievalPolicy(multi_view_enabled=True), reranker_factory=lambda:ranker)
    owner.build_view_index([make_question_view(owner.store.records[0], "login question", "en", "test")])
    base = owner.search_with_trace("login", 2)
    ranker.rerank.assert_not_called()
    supplemented = owner.search_with_trace("login", 2, supplement=True)
    assert supplemented["trace"]["supplement_passes"] == 1
    assert supplemented["trace"]["multi_view"] == "used"
    assert all("fabricated" not in r["content"] for r in supplemented["results"])
    ranker.rerank.side_effect = RuntimeError("offline")
    fallback = owner.search_with_trace("login", 2, supplement=True)
    assert fallback["results"] == base["results"]
    assert fallback["trace"]["fallback_reason"].startswith("reranker_error")


def test_purge_erases_assets_revokes_snapshots_and_cannot_restore(rag_factory):
    source = write(rag_factory)
    write(rag_factory,"other.md","# Other\n\nUnrelated material stays available.")
    owner = rag_factory(cache_enabled=True)
    document = next(d for d in owner.documents if d.filename == source.name)
    original = owner.repository.current_pointer()
    pinned = owner.pipeline
    result = owner.purge_document(document.document_id)
    assert result["status"] == "completed"
    assert not source.exists()
    assert not Path(document.source_blob_path).exists()
    assert owner.registry.list_versions(document.document_id) == []
    assert all(r["document_id"] != document.document_id for r in pinned.search_rankings("login",5)["parents"])
    assert owner.search("Unrelated", 1)
    assert not (owner.repository.root / original["generation"]).exists()
    with pytest.raises(ValueError): owner.rollback_generation(original["generation"])
    with pytest.raises(ValueError): owner.search_with_trace("login", as_of=original["published_at"])
    with pytest.raises(ValueError, match="Purged"): owner.lifecycle.restore(document.document_id)
    assert owner.purge_document(document.document_id) == result


def test_purge_preserves_shared_blobs_and_resumes_failed_cleanup(rag_factory, monkeypatch):
    from app.rag.lifecycle import purge
    a = write(rag_factory,"a.md")
    write(rag_factory,"b.md",a.read_text(encoding="utf-8"))
    owner = rag_factory()
    document = owner.documents[0]
    remove = purge.remove_managed
    counter = [0]
    def fail_once(*args):
        counter[0] += 1
        if counter[0] == 1: raise OSError("injected cleanup interruption")
        return remove(*args)
    monkeypatch.setattr(purge,"remove_managed",fail_once)
    with pytest.raises(OSError): owner.purge_document(document.document_id)
    assert owner.registry.get_document(document.document_id).purged_at
    client = http(owner, monkeypatch)
    listing = client.get("/knowledge/documents").json()
    state = next(d for d in listing if d["document_id"] == document.document_id)
    assert state["purge_state"] == "failed" and state["processing_status"] == "purge_incomplete"
    assert all(r["document_id"] != document.document_id for r in owner.search("login",5))
    assert owner.purge_document(document.document_id)["status"] == "completed"
    assert Path(document.source_blob_path).exists()  # Other logical document still owns these bytes.
    assert owner.search("login",1)


def test_external_source_purge_does_not_delete_user_original_or_reimport(rag_factory, tmp_path):
    external = tmp_path / "external.md"
    external.write_text("# External\n\nExternal login evidence.", encoding="utf-8")
    owner = rag_factory(build=False)
    document, _ = owner.lifecycle.import_document(external)
    owner.build_index()
    assert owner.documents[0].document_id == document.document_id
    assert owner.purge_document(document.document_id)["external_original_preserved"]
    assert external.exists()
    with pytest.raises(ValueError,match="purged"): owner.lifecycle.import_document(external)
    owner.build_index()
    assert owner.documents == []


def http(owner, monkeypatch):
    monkeypatch.setenv("RAG_ADMIN_TOKEN","local-test-token")
    app = FastAPI()
    app.include_router(create_knowledge_router(owner))
    return TestClient(app,headers={"Authorization":"Bearer local-test-token"})


def test_management_api_upload_settings_build_history_and_search(rag_factory, monkeypatch):
    owner = rag_factory(build=False)
    client = http(owner,monkeypatch)
    assert client.get("/knowledge/documents",headers={"Authorization":"bad"}).status_code == 401
    assert client.post("/knowledge/build",headers={"Origin":"https://evil.example"}).status_code == 403
    uploaded = client.post("/knowledge/documents?filename=guide.md",content=b"# Guide\n\nLogin evidence.")
    assert uploaded.status_code == 201, uploaded.text
    document_id = uploaded.json()["document"]["document_id"]
    assert client.patch(f"/knowledge/documents/{document_id}",json={"metadata":{"domain":"general"},"view_config":{"enabled":False}}).status_code == 200
    assert client.post("/knowledge/build").status_code == 202
    owner._build_future.result(timeout=10)
    assert client.get("/knowledge/search?q=login&include_trace=true").json()["results"]
    first = client.get("/knowledge/status").json()["current"]["published_at"]
    assert client.get("/knowledge/search",params={"q":"login","as_of":first}).json()["results"]
    assert client.get("/knowledge/documents").json()[0]["metadata"]["domain"] == "general"
    assert client.get(f"/knowledge/documents/{document_id}/source").status_code == 200
    assert client.get("/knowledge/admin").status_code == 200
    assert client.get("/knowledge/generations").json()["publications"]
    policy = client.get("/knowledge/policy").json()
    policy["multi_view_enabled"] = True
    assert client.put("/knowledge/policy",json=policy).status_code == 200
    assert rag_factory(build=False).orchestrator.policy.multi_view_enabled
    assert client.request("DELETE",f"/knowledge/documents/{document_id}/purge",json={"confirm":False}).status_code == 422


def test_api_upload_bounds_and_no_implicit_cold_build(rag_factory, monkeypatch):
    owner = rag_factory(build=False,auto_build=False)
    client = http(owner,monkeypatch)
    assert client.get("/knowledge/search?q=login").status_code == 409
    assert client.post("/knowledge/documents?filename=../bad.md",content=b"bad").status_code == 422
    assert client.post("/knowledge/documents?filename=bad.txt",content=b"bad").status_code == 422
    monkeypatch.setenv("RAG_UPLOAD_MAX_BYTES","3")
    assert client.post("/knowledge/documents?filename=big.md",content=b"four").status_code == 413
    assert not list((rag_factory.knowledge / "uploads").glob("*.upload"))


def test_restore_version_works_after_source_file_is_missing(rag_factory):
    source = write(rag_factory)
    owner = rag_factory()
    document = owner.documents[0]
    source.unlink()
    owner.restore_version(document.document_id, document.version_id)
    owner.build_index()
    assert owner.search("login", 1)
    assert not source.exists()


def test_llm_optional_supplement_tool_is_bounded_to_one_call(rag_factory):
    from app.services.investigation_service import InvestigationService
    write(rag_factory)
    owner = rag_factory(retrieval_policy=RetrievalPolicy(multi_view_enabled=True))
    owner.search_with_trace = Mock(wraps=owner.search_with_trace)
    llm = Mock()
    calls = [{"id":str(i), "name":"knowledge_supplement", "arguments":json.dumps({"query":"login"})} for i in range(2)]
    llm.chat.side_effect = [
        {"tool_calls":calls,"assistant_message":{"role":"assistant","content":"","tool_calls":[]}},
        {"tool_calls":[],"content":json.dumps({"attack_type":"unconfirmed","confidence":0.1,"evidence":[],"recommendations":[]})},
    ]
    InvestigationService(owner,llm)._run_tool_loop("Inspect evidence",[],[])
    assert owner.search_with_trace.call_count == 1
    messages = llm.chat.call_args.kwargs["messages"]
    tool_outputs = [json.loads(m["content"]) for m in messages if m["role"] == "tool"]
    assert tool_outputs[0]["ok"] and not tool_outputs[1]["ok"]


def test_purge_removes_unpublished_and_interrupted_derived_text(rag_factory):
    write(rag_factory)
    owner = rag_factory(cache_enabled=True)
    identity = owner.documents[0].document_id
    orphan = owner.repository.root / ("f" * 32)
    orphan.mkdir()
    (orphan / "chunks.jsonl").write_text("unpublished sensitive text", encoding="utf-8")
    empty_artifact = rag_factory.storage / "artifacts" / ("e" * 64 + ".json")
    empty_artifact.write_text(json.dumps({"payload":{"title":"unpublished source title","parents":[],"children":[]}}),encoding="utf-8")
    temporary = rag_factory.storage / "views" / ".interrupted.tmp"
    temporary.parent.mkdir(exist_ok=True)
    temporary.write_text("interrupted question text",encoding="utf-8")
    assert owner.purge_document(identity)["status"] == "completed"
    assert not orphan.exists() and not empty_artifact.exists() and not temporary.exists()


def test_no_token_administration_rejects_rebinding_host(rag_factory, monkeypatch):
    monkeypatch.delenv("RAG_ADMIN_TOKEN", raising=False)
    app = FastAPI()
    app.include_router(create_knowledge_router(rag_factory(build=False)))
    client = TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 12345))
    assert client.get("/knowledge/documents").status_code == 200
    assert client.get("/knowledge/documents",headers={"Host":"evil.example"}).status_code == 403


def test_recovery_does_not_confuse_purge_publication_with_completed_erasure(rag_factory):
    write(rag_factory)
    owner = rag_factory()
    current = owner.repository.current_pointer()["generation"]
    job = owner.registry.start_job("purge", current)
    owner.registry.update_job_output(job, owner.registry.revision, current)
    assert owner.build_service.recover()
    recovered = next(item for item in owner.registry.list_jobs() if item["job_id"] == job)
    assert recovered["status"] == "failed" and recovered["error_code"] == "InterruptedMaintenance"
