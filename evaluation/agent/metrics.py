"""Keep execution, semantic review and reported usage separate; never invent billed cost."""
from evaluation.agent.judges import diagnose, validate_reviews


def summarize(rows, reviews=None, *, input_price=None, output_price=None):
    reviews = reviews or {}
    validate_reviews(reviews, [row["case_id"] for row in rows])
    diagnostics = {row["case_id"]: diagnose(row) for row in rows}
    calls = [c for row in rows for c in row["llm_calls"] if c["attempted"]]
    usages = [c.get("response", {}).get("usage") for c in calls]
    known = [u for u in usages if isinstance(u, dict) and all(
        type(u.get(key)) is int and u[key] >= 0 for key in ("prompt_tokens", "completion_tokens"))]
    prompt = sum(u.get("prompt_tokens", 0) for u in known)
    completion = sum(u.get("completion_tokens", 0) for u in known)
    complete = bool(calls) and len(known) == len(calls)
    estimate = None
    if complete and input_price is not None and output_price is not None:
        estimate = (prompt * input_price + completion * output_price) / 1_000_000
    return {"cases": len(rows), "execution_ok": sum(d["execution_ok"] for d in diagnostics.values()),
            "schema_ok": sum(d["schema_ok"] for d in diagnostics.values()), "diagnostics": diagnostics,
            "reviewed_cases": len(reviews), "human_reviewed_cases": sum(r["reviewer_type"] == "human" for r in reviews.values()),
            "semantic_pass_cases": sum(all(d["verdict"] == "pass" for d in r["dimensions"].values()) for r in reviews.values()),
            "semantic_fail_cases": sum(any(d["verdict"] == "fail" for d in r["dimensions"].values()) for r in reviews.values()),
            "usage": {"attempted_requests": len(calls), "responses_with_usage": len(known), "requests_with_unknown_usage": len(calls) - len(known), "complete": complete,
                      "reported_prompt_tokens": prompt, "reported_completion_tokens": completion,
                      "estimated_cost_in_price_units": estimate, "billed_cost": None,
                      "note": "User-supplied per-million-token prices only; discounts and provider billing are not inferred."}}
