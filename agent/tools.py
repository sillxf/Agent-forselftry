"""Read-only tools. Code validates arguments, enforces budgets and wraps results.

Every result has one shape: {call_id, tool, status, retryable, data, note}.
status: ok, empty (a successful search returned no items), a specific service failure,
or rejected (refused by policy or invalid arguments).
"""

import hashlib
import json
from datetime import datetime, timedelta

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from agent.knowledge import KnowledgeUnavailable, safe_trace
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
        state.tool_call_requests += 1
        if state.tool_call_requests > self.budget.max_tool_calls:
            return dict(result, status="rejected", note="Tool request budget exhausted; write the report.")
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
        handlers = {
            "search_alerts": (SearchAlertsArgs, self._search_alerts),
            "knowledge_search": (KnowledgeSearchArgs, self._knowledge_search),
            "get_evidence": (GetEvidenceArgs, self._get_evidence),
        }
        selected = handlers.get(name)
        if selected is None:
            return dict(result, status="rejected", note=f"Unknown tool {name!r}.")
        argument_model, handler = selected
        try:
            argument_model.model_validate(arguments)
        except ValidationError as exc:
            problems = "; ".join(
                f"{'.'.join(map(str, e['loc'])) or 'arguments'}: {e['msg']}" for e in exc.errors()
            )
            return dict(result, status="rejected", note="Invalid arguments: " + problems)
        state.tool_calls += 1
        state.fingerprints[fingerprint] = call_id
        try:
            outcome = handler(arguments)
        except Exception as exc:
            outcome = dict(
                status="service_error",
                error_category="tool_error",
                retryable=False,
                note=f"Tool failed ({type(exc).__name__}); no result was established.",
            )
        if outcome["status"] != "rejected":
            # The call itself is an observation, so "searched X and found nothing"
            # can be cited instead of being attributed to the alert.
            source_id = f"obs:tool:{call_id}"
            data = outcome.get("data")
            observation = dict(
                tool=name, arguments=safe_arguments(name, arguments), status=outcome["status"]
            )
            if data is not None:
                observation["results"] = len(data) if isinstance(data, list) else 1
            state.observations[source_id] = observation
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
            response = self.knowledge.search(
                query, queries=queries, top_k=top_k, include_trace=True
            )
        except KnowledgeUnavailable as exc:
            return dict(
                status=exc.category,
                error_category=exc.category,
                retryable=exc.retryable,
                note=f"Knowledge service {exc.category}; no knowledge was retrieved.",
                diagnostics=_rag_diagnostics(exc.diagnostics, []),
            )
        except Exception as exc:
            category = "invalid_response" if isinstance(exc, (ValueError, TypeError)) else "service_error"
            return dict(
                status="service_error", error_category=category, retryable=False,
                data=None,
                note=f"Knowledge service response could not be processed ({type(exc).__name__}); no result was established.",
                diagnostics=_rag_diagnostics({}, []),
            )
        if not isinstance(response, dict) or not isinstance(response.get("results"), list):
            return dict(
                status="service_error", error_category="invalid_response", retryable=False,
                data=None, note="Knowledge service returned an invalid response; no result was established.",
                diagnostics=_rag_diagnostics(response if isinstance(response, dict) else {}, []),
            )
        items, evidence = [], {}
        try:
            for result in response["results"]:
                if not isinstance(result, dict) or not result.get("chunk_id") or not isinstance(result.get("content"), str):
                    raise ValueError("invalid evidence item")
                source_id = "ev:" + str(result["chunk_id"])
                evidence[source_id] = result
                items.append(
                    dict(
                        source_id=source_id,
                        source=result.get("source") or result.get("source_name"),
                        section=" > ".join(result.get("section_path") or []),
                        pages=[result.get("page_start"), result.get("page_end")],
                        citation=result.get("citation"),
                        generation_id=result.get("generation_id"),
                        relevance=result.get("relevance"),
                        relevance_source=result.get("relevance_source"),
                        # Bounded preview; get_evidence returns the full text.
                        text=result["content"][:1500],
                        truncated=len(result["content"]) > 1500,
                    )
                )
        except (TypeError, ValueError):
            return dict(
                status="service_error", error_category="invalid_response", retryable=False,
                data=None, note="Knowledge service returned an invalid evidence item; no result was established.",
                diagnostics=_rag_diagnostics(response, []),
            )
        self.state.evidence.update(evidence)
        diagnostics = _rag_diagnostics(response, items)
        if diagnostics["unpublished_knowledge_bases"]:
            if items:
                return dict(
                    status="partial", error_category="not_published", data=items,
                    note="Search was partial because one or more knowledge bases were not published; returned evidence covers only available bases.",
                    diagnostics=diagnostics,
                )
            return dict(
                status="partial_empty", error_category="not_published", data=[],
                note="Search was partial because one or more knowledge bases were not published; no items returned from available bases.",
                diagnostics=diagnostics,
            )
        if not items:
            return dict(status="empty", data=[], note="No matching knowledge.", diagnostics=diagnostics)
        return dict(status="ok", data=items, note="Reference material, not alert evidence.", diagnostics=diagnostics)

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


def safe_arguments(name, raw):
    """Summarize parameters without persisting alert identifiers or free text."""
    import hashlib

    if isinstance(raw, str):
        try:
            values = json.loads(raw or "{}")
        except ValueError:
            values = None
    else:
        values = raw
    if not isinstance(values, dict):
        text = raw if isinstance(raw, str) else json.dumps(raw, default=str)
        return {"valid_json_object": False, "sha256": hashlib.sha256(text.encode()).hexdigest()[:16]}

    def digest(value):
        text = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    if name == "search_alerts":
        summary = {"filter_keys": sorted(values)}
        for key in ("source_ip", "asset_id"):
            if values.get(key) is not None:
                summary[key + "_sha256"] = digest(values[key])
        for key in ("severity", "window_minutes"):
            if values.get(key) is not None:
                summary[key] = values[key]
        return summary
    if name == "knowledge_search":
        queries = values.get("queries") if isinstance(values.get("queries"), list) else []
        return {
            "query_sha256": digest(values.get("query")),
            "query_characters": len(values.get("query", "")) if isinstance(values.get("query"), str) else None,
            "rewrite_count": len(queries),
            "rewrite_sha256": [digest(value) for value in queries],
            "top_k": values.get("top_k"),
        }
    if name == "get_evidence":
        return {"evidence_id": values.get("evidence_id")}
    return {"parameter_keys": sorted(values), "parameter_count": len(values)}


def _rag_diagnostics(response, items):
    response = response if isinstance(response, dict) else {}
    metadata = response.get("metadata") if isinstance(response.get("metadata"), dict) else {}
    warnings = metadata.get("warnings") if isinstance(metadata.get("warnings"), list) else []
    unpublished = [
        warning.split(":", 1)[1]
        for warning in warnings
        if isinstance(warning, str) and warning.startswith("not_published:")
    ]
    trace_present = "trace" in response and response.get("trace") is not None
    trace = safe_trace(response.get("trace")) if trace_present else None
    generation_ids, request_ids, configuration_revisions = [], [], []
    value = response.get("request_id") or metadata.get("request_id")
    if value:
        request_ids.append(value)
    for value in (response.get("generation_id"), metadata.get("generation_id")):
        if value and value not in generation_ids:
            generation_ids.append(value)
    trace_items = trace if isinstance(trace, list) else [trace] if isinstance(trace, dict) else []
    snapshots = metadata.get("snapshots") if isinstance(metadata.get("snapshots"), list) else []
    for item in [*trace_items, *snapshots]:
        if not isinstance(item, dict):
            continue
        for value, destination in (
            (item.get("request_id"), request_ids),
            (item.get("generation_id"), generation_ids),
        ):
            if value and value not in destination:
                destination.append(value)
        if item.get("configuration_revision") is not None:
            revision = {
                key: item.get(key)
                for key in ("knowledge_base_id", "configuration_revision")
                if item.get(key) is not None
            }
            if revision not in configuration_revisions:
                configuration_revisions.append(revision)
    for item in items:
        value = item.get("generation_id")
        if value and value not in generation_ids:
            generation_ids.append(value)
    return dict(
        request_id=request_ids[0] if len(request_ids) == 1 else None,
        request_ids=request_ids,
        include_trace_requested=True,
        generation_id=generation_ids[0] if len(generation_ids) == 1 else None,
        generation_ids=generation_ids,
        configuration_revisions=configuration_revisions,
        warnings=safe_trace(warnings),
        unpublished_knowledge_bases=unpublished,
        trace_status="available" if trace_present else "unavailable",
        trace=trace,
        evidence_ids=[item["source_id"] for item in items],
        references=[
            {key: item.get(key) for key in (
                "source_id", "source", "section", "pages", "citation",
                "generation_id", "relevance", "relevance_source"
            )}
            for item in items
        ],
    )
