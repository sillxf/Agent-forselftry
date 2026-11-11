"""Deterministic diagnostics only; semantic correctness requires an explicit review."""
from pydantic import ValidationError

from app.schemas.analysis import SecurityAnalysis

DIMENSIONS = ("alert_understanding", "evidence_grounding", "hallucination", "risk_assessment", "response_quality", "abstention")


def diagnose(row):
    result = row.get("result")
    schema_ok = False
    if result is not None:
        try:
            SecurityAnalysis.model_validate(result["analysis"])
            schema_ok = True
        except ValidationError:
            pass
    calls = [c for c in row["llm_calls"] if c["attempted"]]
    searches = row["retrieval_calls"]
    tool_calls = [t for c in calls for t in c.get("response", {}).get("tool_calls", [])]
    tool_results = row["tool_observations"]
    final = result["analysis"] if result else {}
    text = " ".join(final.get("evidence", []) + final.get("recommendations", []) + [final.get("attack_type", "")]).casefold()
    # Exact matches are review hints, NOT automatic hallucination verdicts (negation/paraphrases exist).
    hints = [claim for claim in row["expected"].get("forbidden_claims", []) if claim.casefold() in text]
    evidence_chars = sum(len(r["content"]) for r in result["knowledge"]) if result else None
    return {"execution_ok": row["error"] is None, "schema_ok": schema_ok,
            "knowledge_searches": len(searches), "llm_attempts": len(calls), "tool_calls": len(tool_calls),
            "tool_errors": sum(not t["ok"] for t in tool_results),
            "knowledge_budget_ok": len(searches) <= 3, "tool_budget_ok": len(tool_calls) <= 12,
            "returned_evidence_chars": evidence_chars,
            "evidence_budget_ok": evidence_chars is not None and evidence_chars <= 24000,
            "exact_forbidden_claim_hints": hints, "semantic_verdict": "not_automatically_judged"}


def validate_reviews(reviews, case_ids):
    if set(reviews) - set(case_ids):
        raise ValueError("Review references unknown cases")
    for review in reviews.values():
        if review.get("reviewer_type") not in {"human", "ai_development"} or not review.get("reviewer"):
            raise ValueError("Review must identify reviewer and distinguish AI development review from human approval")
        dimensions = review.get("dimensions", {})
        if set(dimensions) != set(DIMENSIONS):
            raise ValueError("Review must explicitly cover every semantic dimension")
        if any(item.get("verdict") not in {"pass", "fail", "uncertain"} or not item.get("reason") for item in dimensions.values()):
            raise ValueError("Each review dimension needs a verdict and an evidence-based reason")
