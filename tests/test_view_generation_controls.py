"""Offline tests for separate View models and bounded request scheduling."""
import json
import sys
from unittest.mock import Mock

import pytest

from scripts import rag_question_views


def arguments(tmp_path, monkeypatch, *, records=1, max_batches=100):
    chunks, output = tmp_path / "chunks.jsonl", tmp_path / "views.jsonl"
    chunks.write_text("".join(json.dumps({"chunk_id": str(i)}) + "\n" for i in range(records)), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["views", "generate", "--chunks", str(chunks), "--output", str(output),
                                    "--batch-size", "1", "--max-batches", str(max_batches)])
    return output


def test_offline_view_model_selection_is_independent(tmp_path, monkeypatch):
    output = arguments(tmp_path, monkeypatch)
    monkeypatch.setenv("RAG_VIEW_LLM_MODEL", "independent-view-model")
    monkeypatch.setenv("RAG_VIEW_LLM_BASE_URL", "https://views.invalid/v1")
    selected = {}
    def factory(_unused, base_url, model):
        selected.update(base_url=base_url, model=model)
        return Mock(model=model)
    monkeypatch.setattr(rag_question_views, "LLMClient", factory)
    monkeypatch.setattr(rag_question_views, "generate_question_views", Mock(return_value=[]))
    rag_question_views.main()
    assert selected == dict(base_url="https://views.invalid/v1", model="independent-view-model")
    manifest = json.loads(output.with_suffix(".manifest.json").read_text(encoding="utf-8"))
    assert manifest["completed"] and manifest["generator_model"] == "independent-view-model"


def test_request_budget_precedes_client_creation(tmp_path, monkeypatch):
    output = arguments(tmp_path, monkeypatch, records=3, max_batches=1)
    factory = Mock(side_effect=AssertionError("no client before preflight"))
    monkeypatch.setattr(rag_question_views, "LLMClient", factory)
    with pytest.raises(SystemExit) as error:
        rag_question_views.main()
    assert error.value.code == 2
    factory.assert_not_called()
    assert not output.exists()


def test_failed_generation_does_not_queue_remaining_batches(tmp_path, monkeypatch):
    output = arguments(tmp_path, monkeypatch, records=5)
    monkeypatch.setattr(rag_question_views, "LLMClient", lambda *args: Mock(model="test"))
    generate = Mock(side_effect=RuntimeError("provider failed"))
    monkeypatch.setattr(rag_question_views, "generate_question_views", generate)
    with pytest.raises(RuntimeError, match="provider failed"):
        rag_question_views.main()
    assert generate.call_count == 1
    manifest = json.loads(output.with_suffix(".manifest.json").read_text(encoding="utf-8"))
    assert not manifest["completed"]
