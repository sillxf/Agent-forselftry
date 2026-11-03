"""Focused delivery checks: paid-call boundaries, real tool tracing and offline review."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.llm.client import LLMClient
from evaluation.agent.benchmark import main
from evaluation.agent.judges import DIMENSIONS, diagnose
from evaluation.agent.metrics import summarize
from evaluation.agent.runner import EvaluationBudgetError, RecordingLLM, load_cases, run_case
from evaluation.rag.migration import compare_runs

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = {"attack_type": "possible_brute_force", "confidence": 0.4,
            "evidence": ["Failed logins only; no successful login is established."],
            "recommendations": ["Verify authentication logs before taking action."]}


def response(*, tools=None, usage=None):
    calls = tools or []
    return {"content": None if calls else json.dumps(ANALYSIS), "tool_calls": calls,
            "assistant_message": {"role": "assistant", "content": None if calls else json.dumps(ANALYSIS),
                                  **({"tool_calls": [{"id": c["id"], "type": "function", "function": {
                                      "name": c["name"], "arguments": c["arguments"]}} for c in calls]} if calls else {})},
            "usage": usage}


def sample_row():
    case = deepcopy(load_cases(ROOT / "tests/agent_evaluation/cases.jsonl")[-1])
    case["forbidden_claims"] = ["GOLD_NOT_FOR_THE_MODEL"]
    client = Mock()
    client.chat.side_effect = [response(tools=[{"id": "empty_lookup", "name": "search_alerts", "arguments": "{}"}]), response()]
    retriever = Mock()
    retriever.search_with_trace.return_value = {"results": [], "trace": {"strategy": "hybrid"}}
    return run_case(case, retriever, RecordingLLM(client, max_calls=2))


def test_client_preserves_defaults_and_exposes_opt_in_limits(monkeypatch):
    sdk = Mock()
    sdk.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(ANALYSIS), tool_calls=[],
                    model_dump=lambda **kwargs: {"role": "assistant", "content": json.dumps(ANALYSIS)}))],
        usage=SimpleNamespace(model_dump=lambda **kwargs: {"prompt_tokens": 20, "completion_tokens": 10}))
    factory = Mock(return_value=sdk)
    monkeypatch.setattr("app.llm.client.OpenAI", factory)
    bounded = LLMClient("test-key", "https://example.invalid", "configured-model", timeout=10, max_retries=0, max_completion_tokens=100)
    assert bounded.chat([])["usage"]["completion_tokens"] == 10
    assert factory.call_args.kwargs["max_retries"] == 0
    assert factory.call_args.kwargs["timeout"] == 10
    assert sdk.chat.completions.create.call_args.kwargs["max_completion_tokens"] == 100
    plain = LLMClient("test-key", "https://example.invalid", "configured-model")
    plain.chat([])
    assert "max_retries" not in factory.call_args.kwargs
    assert "timeout" not in factory.call_args.kwargs
    assert "max_completion_tokens" not in sdk.chat.completions.create.call_args.kwargs


def test_request_and_input_budgets_prevent_extra_calls():
    client = Mock()
    client.chat.return_value = response()
    limited = RecordingLLM(client, max_calls=1)
    limited.chat([])
    with pytest.raises(EvaluationBudgetError):
        limited.chat([])
    assert limited.attempts == client.chat.call_count == 1
    tiny = RecordingLLM(client, max_input_chars=10)
    with pytest.raises(EvaluationBudgetError):
        tiny.chat([{"role": "user", "content": "oversized"}])
    assert tiny.attempts == 0 and client.chat.call_count == 1


def test_failed_request_consumes_budget():
    client = Mock()
    client.chat.side_effect = RuntimeError("transport failed")
    limited = RecordingLLM(client, max_calls=1)
    with pytest.raises(RuntimeError):
        limited.chat([])
    with pytest.raises(EvaluationBudgetError):
        limited.chat([])
    assert client.chat.call_count == limited.attempts == 1


def test_real_service_records_empty_tool_without_gold_leakage():
    row = sample_row()
    assert row["error"] is None
    assert row["tool_observations"] == [{"tool_call_id": "empty_lookup", "ok": True, "result": []}]
    assert "GOLD_NOT_FOR_THE_MODEL" not in json.dumps([c["messages"] for c in row["llm_calls"]])
    assert row["semantic_review_status"] == "pending"
    assert diagnose(row)["semantic_verdict"] == "not_automatically_judged"


def test_unknown_usage_and_unreviewed_answers_are_not_passes_or_free():
    result = summarize([sample_row()], input_price=10, output_price=20)
    assert result["execution_ok"] == 1 and result["reviewed_cases"] == result["semantic_pass_cases"] == 0
    assert result["usage"]["requests_with_unknown_usage"] == 2
    assert not result["usage"]["complete"]
    assert result["usage"]["estimated_cost_in_price_units"] is None
    assert result["usage"]["billed_cost"] is None


def test_review_dimensions_are_required_and_ai_is_not_human():
    row = sample_row()
    review = {"reviewer_type": "ai_development", "reviewer": "development-review", "dimensions": {
        name: {"verdict": "pass", "reason": "Checked the recorded alert, returned tool result and final answer."} for name in DIMENSIONS}}
    result = summarize([row], {row["case_id"]: review})
    assert result["semantic_pass_cases"] == 1 and result["human_reviewed_cases"] == 0
    del review["dimensions"]["abstention"]
    with pytest.raises(ValueError, match="every semantic dimension"):
        summarize([row], {row["case_id"]: review})


def test_replay_needs_no_original_cases_or_live_client(tmp_path, monkeypatch):
    source = tmp_path / "source.jsonl"
    source.write_text(json.dumps(sample_row()) + "\n", encoding="utf-8")
    output = tmp_path / "replayed"
    monkeypatch.setattr("sys.argv", ["agent-eval", "--replay", str(source), "--cases", str(tmp_path / "missing.jsonl"), "--output-dir", str(output)])
    monkeypatch.setattr(LLMClient, "chat", Mock(side_effect=AssertionError("replay must not call an LLM")))
    assert main() == 0
    assert json.loads((output / "summary.json").read_text(encoding="utf-8"))["execution_ok"] == 1


@pytest.mark.parametrize("storage", [ROOT / "app/storage", ROOT / "app/storage/indexes"])
def test_live_refuses_production_storage_before_paid_calls(tmp_path, monkeypatch, storage):
    monkeypatch.setattr("sys.argv", ["agent-eval", "--live", "--storage-dir", str(storage), "--output-dir", str(tmp_path / "out")])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2 and not (tmp_path / "out").exists()


def test_migration_comparison_rejects_changed_evidence_and_metric_regressions():
    baseline = {"served": [{"id": "q", "results": ["original evidence"]}], "units_fingerprint": "same", "counts": {"children": 1},
                "benchmark": [{"question_id": "q", "error": None, "metrics_by_k": {"5": {
                    "child": {"recall": 1.0}, "parent": {"recall": 1.0}}}}]}
    assert compare_runs(baseline, deepcopy(baseline))["passed"]
    changed = deepcopy(baseline)
    changed["served"][0]["results"] = ["different evidence"]
    changed["benchmark"][0]["metrics_by_k"]["5"]["parent"]["recall"] = 0.0
    result = compare_runs(baseline, changed)
    assert not result["passed"] and result["changed_queries"] == ["q"] and len(result["metric_regressions"]) == 1
