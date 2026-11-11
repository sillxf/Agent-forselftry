"""Code-enforced report rules. A claim must cite sources that exist in this run.

Claims that break a rule are downgraded to unverified_hypothesis, never silently
kept; every change is listed in report.verification.
"""

import json
import re

from pydantic import ValidationError

from agent.schemas import Downgrade, ModelReport, Report, Verification

FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.I)


class ReportFormatError(ValueError):
    """The model's final message was not a valid report."""


def parse(text):
    if not isinstance(text, str) or not text.strip():
        raise ReportFormatError("Final message is empty.")
    body = FENCE.sub("", text.strip())
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ReportFormatError(f"Final message is not JSON: {exc.msg}") from exc
    try:
        return ModelReport.model_validate(data)
    except ValidationError as exc:
        problems = "; ".join(
            f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors()[:8]
        )
        raise ReportFormatError("Report does not match the schema: " + problems) from exc


def verify(report: ModelReport, observations: dict, evidence: dict) -> Report:
    verification = Verification()
    known = set(observations) | set(evidence)
    claims = []
    for index, claim in enumerate(report.claims):
        unknown = [s for s in claim.sources if s not in known]
        verification.unknown_sources.extend(s for s in unknown if s not in verification.unknown_sources)
        sources = [s for s in claim.sources if s in known]
        reason = None
        if claim.type == "observed_event" and not any(s.startswith("obs:") for s in sources):
            reason = "observed_event must cite an observation (obs:...)"
        elif claim.type == "reference_knowledge" and not any(s.startswith("ev:") for s in sources):
            reason = "reference_knowledge must cite retrieved evidence (ev:...)"
        elif claim.type == "supported_inference" and not sources:
            reason = "supported_inference must cite at least one existing source"
        if reason and unknown:
            reason += f"; unknown source(s) {unknown}"
        if reason:
            verification.downgraded.append(
                Downgrade(claim_index=index, original_type=claim.type, reason=reason)
            )
            claim = claim.model_copy(update={"type": "unverified_hypothesis"})
        claims.append(claim.model_copy(update={"sources": sources}))
    hypothesis = report.attack_hypothesis
    if hypothesis.status == "confirmed" and not any(c.type == "observed_event" for c in claims):
        verification.hypothesis_adjusted = (
            "confirmed -> suspected: no verified observed_event supports it"
        )
        hypothesis = hypothesis.model_copy(update={"status": "suspected"})
    return Report(
        **report.model_dump(exclude={"claims", "attack_hypothesis"}),
        claims=claims,
        attack_hypothesis=hypothesis,
        verification=verification,
    )
