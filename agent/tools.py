"""Read-only tools. Code validates arguments, enforces budgets and wraps results.

Every result has one shape: {call_id, tool, status, retryable, data, note}.
status: ok (data found), empty (searched, nothing found), error (could not search),
rejected (refused by policy: budget, duplicate call or invalid arguments).
"""

import hashlib
import json
from datetime import datetime, timedelta

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from agent.knowledge import KnowledgeUnavailable
from agent.schemas import Severity

MAX_ALERT_RESULTS = 20


class SearchAlertsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_ip: str | None = Field(None, max_length=100)
    asset_id: str | None = Field(None, max_length=200)
    severity: Severity | None = None
    window_minutes: int | None = Field(None, ge=1, le=10080)


class KnowledgeSearchArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=1, max_length=1000)
    queries: list[str] = Field(default_factory=list, max_length=3)
    top_k: int = Field(5, ge=1, le=8)


class GetEvidenceArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    evidence_id: str = Field(min_length=4, max_length=200)


def _schema(model, description, name):
    schema = model.model_json_schema()
    schema.pop("title", None)
    for value in schema.get("properties", {}).values():
        value.pop("title", None)
    schema["additionalProperties"] = False
    return {
        "type": "function",
        "function": {"name": name, "description": description, "parameters": schema},
    }


DEFINITIONS = [
    _schema(
        SearchAlertsArgs,
        "Find other alerts in the current batch. Filter by source_ip, asset_id, severity, "
        "and window_minutes around the investigated alert's time. Returns structured "
        "alerts (max 20). 'empty' means none matched; it is not proof of no attack.",
        "search_alerts",
    ),
    _schema(
        KnowledgeSearchArgs,
        "Search the security knowledge base for reference material (techniques, detection "
        "and response guidance). Put up to 3 rewrites in queries, e.g. an English version "
        "of a Chinese question, or the documents' own terms. Results are reference "
        "knowledge, not evidence that this alert's events happened. Max 3 searches.",
        "knowledge_search",
    ),
    _schema(
        GetEvidenceArgs,
        "Read the full text of one evidence item already returned by knowledge_search, by "
        "its evidence_id (ev:...). Use it to quote accurately instead of paraphrasing.",
        "get_evidence",
    ),
]


def _alert_view(alert):
    return alert.model_dump(mode="json")


class Toolbox:
    def __init__(self, alert, pool, knowledge, state, budget):
        self.alert, self.pool, self.knowledge = alert, pool, knowledge
        self.state, self.budget = state, budget

    def call(self, name, raw_arguments, call_id):
        state = self.state
        result = dict(call_id=call_id, tool=name, retryable=False, data=None, note=None)
        try:
            arguments = json.loads(raw_arguments or "{}")
            if not isinstance(arguments, dict):
                raise ValueError
        except ValueError:
            return dict(result, status="rejected", note="Arguments must be a JSON object.")
        if state.tool_calls >= self.budget.max_tool_calls:
            return dict(result, status="rejected", note="Tool budget exhausted; write the report.")
        fingerprint = hashlib.sha256(
            json.dumps([name, arguments], sort_keys=True).encode()
        ).hexdigest()
        if fingerprint in state.fingerprints:
            return dict(
                result,
                status="rejected",
                note=f"Same call already made as {state.fingerprints[fingerprint]}; "
                "reuse that result instead of repeating it.",
            )
        handler = {
            "search_alerts": self._search_alerts,
            "knowledge_search": self._knowledge_search,
            "get_evidence": self._get_evidence,
        }.get(name)
        if handler is None:
            return dict(result, status="rejected", note=f"Unknown tool {name!r}.")
        try:
            outcome = handler(arguments)
        except ValidationError as exc:
            problems = "; ".join(
                f"{'.'.join(map(str, e['loc'])) or 'arguments'}: {e['msg']}" for e in exc.errors()
            )
            return dict(result, status="rejected", note="Invalid arguments: " + problems)
        state.tool_calls += 1
        state.fingerprints[fingerprint] = call_id
        if outcome["status"] != "rejected":
            # The call itself is an observation, so "searched X and found nothing"
            # can be cited instead of being attributed to the alert.
            source_id = f"obs:tool:{call_id}"
            data = outcome.get("data")
            state.observations[source_id] = dict(
                tool=name, arguments=arguments, status=outcome["status"],
                results=len(data) if isinstance(data, list) else int(data is not None),
            )
            outcome = dict(outcome, source_id=source_id)
        return dict(result, **outcome)

    def _search_alerts(self, arguments):
        args = SearchAlertsArgs.model_validate(arguments)
        matches = [a for a in self.pool if a.id != self.alert.id]
        if args.source_ip:
            matches = [a for a in matches if a.source_ip == args.source_ip]
        if args.asset_id:
            matches = [a for a in matches if a.asset_id == args.asset_id]
        if args.severity:
            matches = [a for a in matches if a.severity == args.severity]
        if args.window_minutes:
            delta = timedelta(minutes=args.window_minutes)
            matches = [a for a in matches if abs(a.detected_at - self.alert.detected_at) <= delta]
        matches.sort(key=lambda a: a.detected_at)
        truncated = len(matches) > MAX_ALERT_RESULTS
        matches = matches[:MAX_ALERT_RESULTS]
        for a in matches:
            self.state.observations[f"obs:alert:{a.id}"] = _alert_view(a)
        if not matches:
            return dict(status="empty", data=[], note="No other alert in this batch matched.")
        return dict(
            status="ok",
            data=[dict(source_id=f"obs:alert:{a.id}", **_alert_view(a)) for a in matches],
            note="Truncated to 20; narrow the filters." if truncated else None,
        )

    def _knowledge_search(self, arguments):
        args = KnowledgeSearchArgs.model_validate(arguments)
        if self.state.knowledge_searches >= self.budget.max_knowledge_searches:
            return dict(status="rejected", note="Knowledge search budget exhausted.")
        self.state.knowledge_searches += 1
        return self.search_knowledge(args.query, args.queries, args.top_k)

    def search_knowledge(self, query, queries=(), top_k=5):
        try:
            response = self.knowledge.search(query, queries=queries, top_k=top_k)
        except KnowledgeUnavailable as exc:
            return dict(
                status="error",
                retryable=exc.retryable,
                note=f"Knowledge service {exc.category}; no knowledge was retrieved.",
            )
        items = []
        for result in response.get("results", []):
            source_id = "ev:" + result["chunk_id"]
            self.state.evidence[source_id] = result
            items.append(
                dict(
                    source_id=source_id,
                    source=result.get("source") or result.get("source_name"),
                    section=" > ".join(result.get("section_path") or []),
                    pages=[result.get("page_start"), result.get("page_end")],
                    # Bounded preview; get_evidence returns the full text.
                    text=result["content"][:1500],
                    truncated=len(result["content"]) > 1500,
                )
            )
        if not items:
            return dict(status="empty", data=[], note="No matching knowledge.")
        return dict(status="ok", data=items, note="Reference material, not alert evidence.")

    def _get_evidence(self, arguments):
        args = GetEvidenceArgs.model_validate(arguments)
        item = self.state.evidence.get(args.evidence_id)
        if item is None:
            return dict(
                status="rejected",
                note="Unknown evidence_id; only items returned by knowledge_search exist.",
            )
        return dict(
            status="ok",
            data=dict(
                source_id=args.evidence_id,
                source=item.get("source"),
                section=" > ".join(item.get("section_path") or []),
                citation=item.get("citation"),
                text=item["content"][:8000],
            ),
        )


def timestamp():
    return datetime.now().isoformat(timespec="seconds")
