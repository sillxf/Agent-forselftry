"""Optional reranking never owns evidence, resource budgets or fallback decisions."""
import json
from threading import Event
from unittest.mock import Mock

import pytest

from app.rag.retrieval.policy import RetrievalPolicy
from app.services.investigation_service import InvestigationService, ToolCallLimitError


def source(factory):
    (factory.knowledge / "manual.md").write_text("# Detection\n\nRepeated failed login attempts.", encoding="utf-8")


def test_default_policy_is_hybrid_and_does_not_load_optional_models(rag_factory):
    source(rag_factory)
    factory = Mock(side_effect=AssertionError("no optional model on default route"))
    retriever = rag_factory(reranker_factory=factory)
    detailed = retriever.search_with_trace("login", 5)
    assert detailed["results"] == retriever.search_rankings("login", 5)["parents"]
    assert detailed["trace"]["strategy"] == "hybrid"
    assert detailed["trace"]["multi_view"] == "disabled"
    assert detailed["trace"]["generation_id"] == retriever._generation_id
    factory.assert_not_called()


def test_optional_reranker_cannot_modify_canonical_evidence(rag_factory):
    source(rag_factory)
    def rerank(query, candidates):
        candidates[0]["content"] = "fabricated text"
        return [dict(item, reranker_score=1) for item in reversed(candidates)]
    ranker = Mock(rerank=Mock(side_effect=rerank))
    retriever = rag_factory(retrieval_policy=RetrievalPolicy(default_strategy="hybrid_rerank"),
                            reranker_factory=lambda: ranker)
    detailed = retriever.search_with_trace("login", 5)
    assert detailed["trace"]["reranker_used"]
    assert all("fabricated" not in item["content"] for item in detailed["results"])
    assert "failed login" in detailed["results"][0]["content"]


@pytest.mark.parametrize("output", [RuntimeError("offline"), [{"chunk_id": "invented"}], [{"chunk_id": "unused", "reranker_score": float("nan")} ]])
def test_optional_reranker_failure_keeps_primary_evidence(rag_factory, output):
    source(rag_factory)
    ranker = Mock()
    if isinstance(output, Exception):
        ranker.rerank.side_effect = output
    else:
        ranker.rerank.return_value = output
    retriever = rag_factory(retrieval_policy=RetrievalPolicy(default_strategy="hybrid_rerank"),
                            reranker_factory=lambda: ranker)
    detailed = retriever.search_with_trace("login", 5)
    assert not detailed["trace"]["reranker_used"]
    assert detailed["trace"]["fallback_reason"].startswith("reranker_error")
    assert detailed["results"]


def test_timeout_falls_back_and_does_not_queue_more_reranking_work(rag_factory):
    source(rag_factory)
    release = Event()
    def slow(query, candidates):
        assert release.wait(10)
        return candidates
    ranker = Mock(rerank=Mock(side_effect=slow))
    retriever = rag_factory(retrieval_policy=RetrievalPolicy(default_strategy="hybrid_rerank", reranker_timeout_seconds=0.01),
                            reranker_factory=lambda: ranker)
    try:
        first = retriever.search_with_trace("login", 5)
        second = retriever.search_with_trace("login", 5)
        assert first["results"] and second["results"]
        assert first["trace"]["fallback_reason"] == "reranker_timeout"
        assert second["trace"]["fallback_reason"] == "reranker_busy"
        assert ranker.rerank.call_count == 1
    finally:
        release.set()
        retriever.orchestrator._future.result(timeout=10)


def test_live_delete_is_rechecked_after_reranking(rag_factory):
    source(rag_factory)
    holder = {}
    def rerank(query, candidates):
        owner = holder["retriever"]
        owner.lifecycle.delete(owner.documents[0].document_id)
        return candidates
    ranker = Mock(rerank=Mock(side_effect=rerank))
    retriever = rag_factory(retrieval_policy=RetrievalPolicy(default_strategy="hybrid_rerank"), reranker_factory=lambda: ranker)
    holder["retriever"] = retriever
    assert retriever.search("login", 5) == []


def test_context_budget_never_slices_an_evidence_chunk(rag_factory):
    source(rag_factory)
    retriever = rag_factory(retrieval_policy=RetrievalPolicy(max_context_chars=10))
    result = retriever.search_with_trace("login", 5)
    assert result["trace"]["context_chars"] <= 10
    assert result["results"] == []
    with pytest.raises(ValueError, match="character budget"):
        retriever.search("x" * 4001, 1)


def test_agent_search_budget_includes_initial_retrieval(rag_factory):
    from app.main import load_alerts
    source(rag_factory)
    retriever = rag_factory()
    retriever.search = Mock(wraps=retriever.search)
    calls = [{"id": str(i), "name": "knowledge_search", "arguments": json.dumps({"query": "login"})} for i in range(4)]
    llm = Mock()
    llm.chat.side_effect = [
        {"tool_calls": calls, "assistant_message": {"role": "assistant", "content": ""}},
        {"tool_calls": [], "content": json.dumps(dict(attack_type="test", confidence=0.1, evidence=[], recommendations=[]))},
    ]
    InvestigationService(retriever, llm).investigate(load_alerts()[0])
    assert retriever.search.call_count == 3
    messages = llm.chat.call_args.kwargs["messages"]
    outputs = [json.loads(message["content"]) for message in messages if message["role"] == "tool"]
    assert sum(not output["ok"] for output in outputs) == 2
    assert all("budget" in output["error"] for output in outputs if not output["ok"])


def test_agent_also_caps_total_calls_within_a_single_round(rag_factory):
    from app.main import load_alerts
    source(rag_factory)
    retriever = rag_factory()
    calls = [{"id": str(i), "name": "unknown", "arguments": "{}"} for i in range(13)]
    llm = Mock()
    llm.chat.return_value = {"tool_calls": calls, "assistant_message": {"role": "assistant", "content": ""}}
    with pytest.raises(ToolCallLimitError, match="Total tool-call budget"):
        InvestigationService(retriever, llm).investigate(load_alerts()[0])


def test_http_trace_and_input_cost_boundaries(rag_factory, monkeypatch):
    from fastapi.testclient import TestClient
    import app.main as main
    source(rag_factory)
    retriever = rag_factory()
    monkeypatch.setattr(main, "knowledge_retriever", retriever)
    client = TestClient(main.app)
    response = client.get("/knowledge/search", params={"q": "login", "include_trace": True})
    assert response.status_code == 200 and response.json()["results"]
    assert response.json()["trace"]["generation_id"] == retriever._generation_id
    assert client.get("/knowledge/search", params={"q": "x" * 4001}).status_code == 422
    assert client.get("/knowledge/search", params={"q": "login", "k": 1000}).status_code == 422
