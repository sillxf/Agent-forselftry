"""Run the real read-only investigation service; gold labels never enter model input."""
from copy import deepcopy
import json
import time
from pathlib import Path

from app.schemas.alert import Alert
from app.services.investigation_service import InvestigationService


class EvaluationBudgetError(RuntimeError):
    pass


class RecordingLLM:
    def __init__(self, client, *, max_calls=12, max_input_chars=60000):
        if max_calls <= 0 or max_input_chars <= 0:
            raise ValueError("Evaluation budgets must be positive")
        self.client, self.max_calls, self.max_input_chars = client, max_calls, max_input_chars
        self.attempts = 0
        self.calls = []

    def chat(self, messages, tools=None):
        record = {"messages": deepcopy(messages), "tools": deepcopy(tools), "attempted": False}
        self.calls.append(record)
        size = len(json.dumps({"messages": messages, "tools": tools}, ensure_ascii=False))
        if self.attempts >= self.max_calls or size > self.max_input_chars:
            record["error"] = "EvaluationBudgetError"
            raise EvaluationBudgetError("Evaluation request-count or input-character budget exhausted")
        self.attempts += 1
        record["attempted"] = True
        start = time.perf_counter()
        try:
            response = self.client.chat(messages=messages, tools=tools)
            record["response"] = deepcopy(response)
            return response
        except Exception as exc:
            record["error"] = type(exc).__name__
            raise
        finally:
            record["elapsed_ms"] = (time.perf_counter() - start) * 1000


class RecordingRetriever:
    def __init__(self, retriever):
        self.retriever, self.calls = retriever, []

    def search(self, query, k=2):
        start = time.perf_counter()
        record = {"query": query, "k": k}
        self.calls.append(record)
        try:
            response = self.retriever.search_with_trace(query, k)
            record.update(deepcopy(response))
            return response["results"]
        except Exception as exc:
            record["error"] = type(exc).__name__
            raise
        finally:
            record["elapsed_ms"] = (time.perf_counter() - start) * 1000


def load_cases(path):
    cases = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [case["case_id"] for case in cases]
    if not ids or any(not isinstance(key, str) or not key.strip() for key in ids) or len(ids) != len(set(ids)):
        raise ValueError("Cases must have nonempty unique IDs")
    for case in cases:
        Alert.model_validate(case["alert"])
        fixture = case.get("tool_fixture")
        if fixture is not None:
            if set(fixture) != {"related_alerts"} or not isinstance(fixture["related_alerts"], list):
                raise ValueError("Unsupported tool fixture; never silently pretend it was executed")
            for alert in fixture["related_alerts"]:
                Alert.model_validate(alert)
    return cases


def tool_observations(calls):
    results = {}
    for call in calls:
        for message in call["messages"]:
            if message["role"] == "tool":
                results[message["tool_call_id"]] = json.loads(message["content"])
    return [{"tool_call_id": key, **value} for key, value in results.items()]


def run_case(case, retriever, llm):
    observed = RecordingRetriever(retriever)
    start_index = len(llm.calls)
    start = time.perf_counter()
    result, error = None, None
    fixture = case.get("tool_fixture")
    pool = None if fixture is None else [Alert.model_validate(a) for a in fixture["related_alerts"]]
    try:
        result = InvestigationService(observed, llm).investigate(Alert.model_validate(case["alert"]), alert_pool=pool)
        result = {"risk": result["risk"], "knowledge": result["knowledge"], "analysis": result["analysis"].model_dump(mode="json")}
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc)}
    calls = deepcopy(llm.calls[start_index:])
    return {"case_id": case["case_id"], "synthetic": case.get("synthetic", True),
            "input": {"alert": case["alert"], "tool_fixture": fixture},
            "expected": {k: case.get(k) for k in ("observed_event", "supported_inference", "unverified_hypothesis",
                                                   "forbidden_claims", "expected_behavior", "reference_knowledge")},
            "result": result, "error": error, "elapsed_ms": (time.perf_counter() - start) * 1000,
            "retrieval_calls": observed.calls, "llm_calls": calls, "tool_observations": tool_observations(calls),
            "semantic_review_status": "pending"}
