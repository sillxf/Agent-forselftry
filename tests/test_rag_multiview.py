"""Only the new boundaries: source identity, auxiliary ranking, publication and tool access."""
import json
from unittest.mock import Mock

from fastapi.testclient import TestClient
import numpy as np
import pytest

from app.rag.indexing.pipeline import IndexingPipeline
from app.rag.views import generate_question_views, make_question_view, validate_views
from app.rag.retrieval.multiview import MultiViewDenseRetriever
from app.rag.indexing.vector_store import FaissVectorStore
from app.tools.knowledge_tools import execute_knowledge_tool, knowledge_tool_definition


def install_views(retriever):
    records = retriever.store.records
    views = [make_question_view(r, "How to contain a compromised host?", "en", "test/v1") for r in records]
    retriever.build_view_index(views)
    return views


def test_auxiliary_views_are_independent_reloadable_and_do_not_change_hybrid(rag_factory):
    (rag_factory.knowledge / "manual.md").write_text("# Response\n\nIsolate a compromised host.", encoding="utf-8")
    retriever = rag_factory()
    previous = retriever.search_rankings("isolate", 3)
    original_records = list(retriever.store.records)
    pointer = retriever.repository.root / "current.json"
    old_generation = json.loads(pointer.read_text())["generation"]
    views = install_views(retriever)
    assert retriever.retrieval_modes == ("hybrid", "multi_view")
    assert retriever.store.records == original_records
    assert retriever.pipeline.sparse.records == original_records
    assert retriever.search_rankings("isolate", 3) == previous
    result = retriever.search("contain", 1, retrieval_mode="multi_view")[0]
    assert result["content"] == "Response\n\nIsolate a compromised host."
    assert result["chunk_id"] in {r["chunk_id"] for r in original_records}
    assert "How to contain" not in result["content"]
    assert result["matched_view_types"] == ["question"]
    assert set(result["matched_view_ids"]) <= {v.view_id for v in views}
    reloaded = rag_factory(build=False)
    assert reloaded.search("contain", 1, retrieval_mode="multi_view") == [result]
    assert (retriever.repository.root / old_generation / "metadata.db").exists()
    assert json.loads(pointer.read_text())["generation"] != old_generation


def test_view_deduplication_encodes_query_once_and_never_returns_generated_text():
    original = FaissVectorStore(2)
    records = [dict(chunk_id=c, parent_id="p", content=f"source {c}", search_text=f"source {c}") for c in ("a", "b")]
    original.add([[1, 0], [0, 1]], records)
    views = [make_question_view(records[0], "generated question", language, "test") for language in ("zh", "en")]
    auxiliary = FaissVectorStore(2)
    auxiliary.add([[0, 1], [0, 1]], [dict(v.model_dump(), chunk_id=v.view_id) for v in views])
    embed = Mock(return_value=np.array([[0., 1.]], dtype="float32"))
    ranked = MultiViewDenseRetriever(original, auxiliary, embed).retrieve("query", 2)
    embed.assert_called_once_with(["query"])
    assert len(ranked) == 2
    a = next(r for r in ranked if r["chunk_id"] == "a")
    assert a["score"] == 1 / 62 + 1 / 61  # one original vote + one auxiliary vote, not two
    assert a["content"] == a["search_text"] == "source a"
    assert len(a["matched_view_ids"]) == 2


def test_invalid_views_or_failed_preparation_do_not_publish(rag_factory, monkeypatch):
    (rag_factory.knowledge / "manual.md").write_text("# Response\n\nIsolate the host.", encoding="utf-8")
    retriever = rag_factory()
    pointer = retriever.repository.root / "current.json"
    previous_pointer = pointer.read_bytes()
    previous_pipeline = retriever.pipeline
    view = make_question_view(retriever.store.records[0], "Containment?", "en", "test")
    with pytest.raises(ValueError, match="stale"):
        retriever.build_view_index([view.model_copy(update={"source_content_hash": "wrong"})])
    with pytest.raises(ValueError, match="Duplicate"):
        validate_views([view, view], retriever.store.records)
    monkeypatch.setattr(retriever, "_prepare_pipeline", Mock(side_effect=RuntimeError("preparation failed")))
    with pytest.raises(RuntimeError, match="preparation failed"):
        retriever.build_view_index([view])
    assert retriever.pipeline is previous_pipeline
    assert pointer.read_bytes() == previous_pointer


def test_view_model_and_dimension_must_match_original(rag_factory):
    (rag_factory.knowledge / "manual.md").write_text("# Response\n\nIsolate the host.", encoding="utf-8")
    retriever = rag_factory()
    record = retriever.store.records[0]
    view = make_question_view(record, "Containment?", "en", "test")
    from app.rag.indexing.pipeline import IndexSnapshot
    snapshot = IndexSnapshot(retriever.store, retriever.documents, list(retriever.parents.values()))
    with pytest.raises(ValueError, match="dimension"):
        IndexingPipeline(lambda texts: np.zeros((len(texts), 3))).build_views(snapshot, [view], model_name="different")
    snapshot = IndexingPipeline(retriever.embedding_fn).build_views(snapshot, [view], model_name="different")
    with pytest.raises(ValueError, match="same embedding model"):
        retriever.repository.save(snapshot, {"model": retriever.model_name})
    with pytest.raises(ValueError, match="same embedding model"):
        retriever.attach_index(snapshot.store, snapshot.documents, retriever.parents,
                               view_store=snapshot.view_store, view_model_name="different")


def test_offline_generator_uses_only_source_and_resolves_indices_locally():
    record = dict(chunk_id="canonical-id", parent_id="p", search_text="PowerShell can execute commands remotely.")
    llm = Mock(model="generator")
    llm.generate.return_value = json.dumps({"questions": [{"source_index": 0, "zh": "怎样远程执行命令？", "en": "How can commands run remotely?"}]})
    views = generate_question_views([record], llm)
    assert {v.language for v in views} == {"zh", "en"}
    assert all(v.source_child_id == "canonical-id" for v in views)
    assert record["search_text"] in llm.generate.call_args.args[0]
    llm.generate.return_value = '{"questions":[{"source_index":9,"zh":"x","en":"y"}]}'
    with pytest.raises(ValueError, match="unknown"):
        generate_question_views([record], llm)
    llm.generate.return_value = '{"questions":[]}'
    assert generate_question_views([record], llm) == []


def test_http_and_tool_modes_are_explicit_and_unavailable_mode_is_not_a_fallback(rag_factory, monkeypatch):
    import app.main as main
    (rag_factory.knowledge / "manual.md").write_text("# Response\n\nIsolate the host.", encoding="utf-8")
    retriever = rag_factory()
    monkeypatch.setattr(main, "knowledge_retriever", retriever)
    client = TestClient(main.app)
    assert client.get("/knowledge/search", params={"q": "isolate"}).status_code == 200
    assert client.get("/knowledge/search", params={"q": "isolate", "retrieval_mode": "multi_view"}).status_code == 409
    assert client.get("/knowledge/search", params={"q": "isolate", "retrieval_mode": "invalid"}).status_code == 422
    definition = knowledge_tool_definition(retriever.retrieval_modes)
    assert definition["function"]["parameters"]["properties"]["retrieval_mode"]["enum"] == ["hybrid"]
    install_views(retriever)
    output = execute_knowledge_tool({"query": "contain", "retrieval_mode": "multi_view", "top_k": 1}, retriever)
    assert output["retrieval_mode"] == "multi_view" and output["results"]
    assert client.get("/knowledge/search", params={"q": "contain", "retrieval_mode": "multi_view"}).status_code == 200


def test_agent_can_explicitly_call_knowledge_tool_and_returns_its_original_evidence(rag_factory):
    from app.services.investigation_service import InvestigationService
    from app.main import load_alerts
    (rag_factory.knowledge / "manual.md").write_text("# Response\n\nIsolate the compromised host.", encoding="utf-8")
    retriever = rag_factory()
    install_views(retriever)
    llm = Mock()
    llm.chat.side_effect = [
        {"tool_calls": [{"id": "search1", "name": "knowledge_search", "arguments": json.dumps({"query": "contain", "retrieval_mode": "multi_view"})}],
         "assistant_message": {"role": "assistant", "content": ""}},
        {"tool_calls": [], "content": json.dumps({"attack_type": "test", "confidence": 0.5, "evidence": ["Isolate the compromised host."], "recommendations": []})},
    ]
    result = InvestigationService(retriever, llm).investigate(load_alerts()[0])
    assert result["knowledge"]
    tools = llm.chat.call_args_list[0].kwargs["tools"]
    assert tools[-1]["function"]["parameters"]["properties"]["retrieval_mode"]["enum"] == ["hybrid", "multi_view"]
    tool_message = llm.chat.call_args_list[-1].kwargs["messages"][-1]
    evidence = json.loads(tool_message["content"])["result"]["results"][0]
    assert "Isolate" in evidence["content"] and "How to contain" not in evidence["content"]
