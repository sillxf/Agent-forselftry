"""Workflow with one agent node. Code owns stages, budgets and verification."""

from time import perf_counter

from agent import prompt
from agent.schemas import Alert
from agent.state import Budget, InvestigationState
from agent.tools import DEFINITIONS, Toolbox
from agent.triage import duplicates, risk
from agent.verify import ReportFormatError, parse, verify


class Investigator:
    def __init__(self, llm, knowledge, budget=None, *, language=None):
        """llm: object with chat(messages, tools=None) -> {content, tool_calls,
        assistant_message, usage}, as app.models.llm.client.LLMClient provides.
        language: report language; default follows the alert text (English/Chinese)."""
        self.llm, self.knowledge, self.budget = llm, knowledge, budget or Budget()
        self.language = language

    def investigate(self, alert, pool=None):
        # RECEIVED: invalid input raises ValidationError before any call is made.
        alert = Alert.model_validate(alert)
        pool = [Alert.model_validate(a) for a in (pool or [alert])]
        if all(a.id != alert.id for a in pool):
            pool.append(alert)
        state = InvestigationState(alert_id=alert.id)
        try:
            report = self._run(alert, pool, state)
            state.stage = "COMPLETED"
            return self._result(state, report)
        except Exception as exc:  # Keep collected material; never return a bare error.
            state.stage = "FAILED"
            state.failure = f"{type(exc).__name__}: {str(exc)[:300]}"
            return self._result(state, None)

    def _run(self, alert, pool, state):
        state.observations[f"obs:alert:{alert.id}"] = alert.model_dump(mode="json")
        rule = risk(alert, pool)
        state.observations["obs:risk"] = rule
        dups = duplicates(alert, pool)
        for identity in dups:
            other = next(a for a in pool if a.id == identity)
            state.observations[f"obs:alert:{identity}"] = other.model_dump(mode="json")
        toolbox = Toolbox(alert, pool, self.knowledge, state, self.budget)
        started = perf_counter()
        initial = toolbox.search_knowledge(f"{alert.title}. {alert.description}", top_k=3)
        state.knowledge_searches += 1
        state.record(
            kind="tool", name="knowledge_search", status=initial["status"],
            elapsed_ms=(perf_counter() - started) * 1000, note="initial, by code",
        )
        state.stage = "CONTEXT_READY"
        messages = [
            {
                "role": "system",
                "content": prompt.system(self.language or prompt.report_language(alert)),
            },
            {"role": "user", "content": prompt.opening(alert, rule, dups, initial)},
        ]
        state.stage = "INVESTIGATING"
        while True:
            final_turn = (
                state.llm_calls >= self.budget.max_llm_calls - 1
                or state.tool_calls >= self.budget.max_tool_calls
            )
            if final_turn and messages[-1].get("content") != prompt.FINAL_TURN:
                messages.append({"role": "user", "content": prompt.FINAL_TURN})
            if state.llm_calls >= self.budget.max_llm_calls:
                raise RuntimeError("Model call budget exhausted without a valid report")
            response = self._chat(state, messages, None if final_turn else DEFINITIONS)
            if not response["tool_calls"]:
                state.stage = "VERIFYING"
                try:
                    return verify(parse(response["content"]), state.observations, state.evidence)
                except ReportFormatError as exc:
                    if state.report_repairs >= self.budget.max_report_repairs:
                        raise
                    state.report_repairs += 1
                    state.stage = "INVESTIGATING"
                    messages.append({"role": "assistant", "content": response["content"] or ""})
                    messages.append({"role": "user", "content": prompt.repair(exc)})
                    continue
            messages.append(response["assistant_message"])
            for call in response["tool_calls"]:
                started = perf_counter()
                result = toolbox.call(call["name"], call["arguments"], call["id"])
                state.record(
                    kind="tool", name=call["name"], status=result["status"],
                    elapsed_ms=(perf_counter() - started) * 1000,
                    arguments=_safe_arguments(call["arguments"]), call_id=call["id"],
                    note=result.get("note"),
                )
                messages.append(
                    {"role": "tool", "tool_call_id": call["id"], "content": prompt.tool_message(result)}
                )

    def _chat(self, state, messages, tools):
        started = perf_counter()
        state.llm_calls += 1
        try:
            response = self.llm.chat(messages=messages, tools=tools)
        except Exception as exc:
            state.record(
                kind="llm", name="chat", status="error",
                elapsed_ms=(perf_counter() - started) * 1000, note=type(exc).__name__,
            )
            raise
        state.record(
            kind="llm", name="chat",
            status="tool_calls" if response["tool_calls"] else "final",
            elapsed_ms=(perf_counter() - started) * 1000, usage=response.get("usage"),
        )
        return response

    @staticmethod
    def _result(state, report):
        return dict(
            alert_id=state.alert_id,
            stage=state.stage,
            report=report.model_dump(mode="json") if report else None,
            failure=state.failure,
            observations=state.observations,
            evidence={
                key: {k: value.get(k) for k in ("source", "section_path", "citation", "content")}
                for key, value in state.evidence.items()
            },
            steps=[vars(step) for step in state.steps],
            counters=dict(
                tool_calls=state.tool_calls,
                knowledge_searches=state.knowledge_searches,
                report_repairs=state.report_repairs,
            ),
            usage=state.usage(),
        )


def _safe_arguments(raw):
    import json

    try:
        value = json.loads(raw or "{}")
        return value if isinstance(value, dict) else {"_raw": str(raw)[:200]}
    except ValueError:
        return {"_raw": str(raw)[:200]}
