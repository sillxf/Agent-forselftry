"""Explicit investigation state. Kept in code, not in the model's context."""

from dataclasses import dataclass, field
from typing import Literal

Stage = Literal[
    "RECEIVED", "CONTEXT_READY", "INVESTIGATING", "VERIFYING", "COMPLETED", "FAILED"
]


@dataclass(frozen=True)
class Budget:
    max_llm_calls: int = 6
    max_tool_calls: int = 12
    max_knowledge_searches: int = 3
    max_report_repairs: int = 1


@dataclass
class Step:
    step_id: int
    kind: Literal["llm", "tool"]
    name: str
    status: str
    elapsed_ms: float
    arguments: dict | None = None
    call_id: str | None = None
    note: str | None = None
    usage: dict | None = None


@dataclass
class InvestigationState:
    alert_id: str
    stage: Stage = "RECEIVED"
    steps: list[Step] = field(default_factory=list)
    # Stable source IDs the report may cite: "obs:..." for observations, "ev:..." for
    # knowledge evidence. Values are the material the source refers to.
    observations: dict[str, dict] = field(default_factory=dict)
    evidence: dict[str, dict] = field(default_factory=dict)
    llm_calls: int = 0
    tool_calls: int = 0
    knowledge_searches: int = 0
    report_repairs: int = 0
    fingerprints: dict[str, str] = field(default_factory=dict)
    failure: str | None = None

    def record(self, **values):
        step = Step(step_id=len(self.steps) + 1, **values)
        self.steps.append(step)
        return step

    def usage(self):
        reported = [s.usage for s in self.steps if s.kind == "llm" and s.usage]
        calls = sum(1 for s in self.steps if s.kind == "llm")
        return dict(
            llm_calls=calls,
            responses_with_usage=len(reported),
            prompt_tokens=sum(u.get("prompt_tokens") or 0 for u in reported),
            completion_tokens=sum(u.get("completion_tokens") or 0 for u in reported),
            complete=calls == len(reported),
        )
