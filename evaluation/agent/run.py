"""Bounded live smoke run of the agent over the synthetic design cases.

    python -m evaluation.agent.run --live --output evaluation/results/agent-<date>

Without --live nothing is sent to the model. Each case is one investigation with the
agent's own budget (at most 6 model requests). Diagnostics are deterministic: run
status, schema, budgets, downgraded claims, and exact-text hints for forbidden
claims. Exact matches are only hints (negations and paraphrases exist); semantic
correctness needs a review, recorded separately per dimension.
"""

import argparse
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "evaluation/agent/cases.jsonl"


def load_cases(ids=None):
    cases = [json.loads(line) for line in CASES.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [c for c in cases if not ids or c["case_id"] in ids]


def pool(case):
    """The batch the agent may search. A fixture's related alerts are real tool data."""
    fixture = case.get("tool_fixture") or {}
    return [case["alert"], *fixture.get("related_alerts", [])]


def diagnose(case, result):
    report = result["report"] or {}
    text = json.dumps(
        [report.get("summary"), [c["text"] for c in report.get("claims", [])
                                 if c["type"] != "unverified_hypothesis"],
         [r["action"] for r in report.get("recommendations", [])]],
        ensure_ascii=False,
    ).casefold()
    tool_steps = [s for s in result["steps"] if s["kind"] == "tool"]
    return dict(
        stage=result["stage"],
        failure=result["failure"],
        hypothesis=report.get("attack_hypothesis"),
        claims_by_type={
            kind: sum(c["type"] == kind for c in report.get("claims", []))
            for kind in ("observed_event", "reference_knowledge", "supported_inference",
                         "unverified_hypothesis")
        },
        downgraded=len(report.get("verification", {}).get("downgraded", [])),
        unknown_sources=report.get("verification", {}).get("unknown_sources", []),
        hypothesis_adjusted=report.get("verification", {}).get("hypothesis_adjusted"),
        tool_calls=[(s["name"], s["status"]) for s in tool_steps],
        # Provider-reported usage is billed but not verified. Flag calls whose reported
        # prompt is far larger than anything this run sent (observed once: 84,673
        # reported for a ~2k-token request on an OpenAI-compatible proxy).
        usage_anomalies=[
            s["step_id"] for s in result["steps"]
            if s["kind"] == "llm" and (s.get("usage") or {}).get("prompt_tokens", 0) > 40000
        ],
        rejected_tool_calls=sum(s["status"] == "rejected" for s in tool_steps),
        forbidden_claim_hints=[
            claim for claim in case["forbidden_claims"] if claim.casefold() in text
        ],
        usage=result["usage"],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--live", action="store_true", help="Required to call the model")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case-ids", help="Comma-separated subset")
    parser.add_argument("--max-cases", type=int, default=8)
    args = parser.parse_args()
    cases = load_cases(set(args.case_ids.split(",")) if args.case_ids else None)
    if len(cases) > args.max_cases:
        parser.error(f"{len(cases)} cases exceed --max-cases")
    if not args.live:
        print(json.dumps([c["case_id"] for c in cases]))
        print("Dry run: add --live to call the model (up to 6 requests per case).")
        return
    from dotenv import load_dotenv

    load_dotenv()
    from agent.investigator import Investigator
    from agent.knowledge import RAGKnowledge
    from app.models.llm.client import LLMClient

    # Resumable: cases already in runs.jsonl are not sent to the model again.
    args.output.mkdir(parents=True, exist_ok=True)
    runs = args.output / "runs.jsonl"
    done = {
        json.loads(line)["case_id"]
        for line in (runs.read_text(encoding="utf-8").splitlines() if runs.exists() else [])
        if line.strip()
    }
    cases = [c for c in cases if c["case_id"] not in done]
    llm = LLMClient(
        os.getenv("LLM_API_KEY"), os.getenv("LLM_BASE_URL"), os.getenv("LLM_MODEL"),
        timeout=90, max_retries=1, max_completion_tokens=4096,
    )
    knowledge = RAGKnowledge()
    try:
        for case in cases:
            started = time.perf_counter()
            result = Investigator(llm, knowledge).investigate(case["alert"], pool(case))
            row = dict(
                case_id=case["case_id"],
                elapsed_s=round(time.perf_counter() - started, 1),
                diagnostics=diagnose(case, result),
                result=result,
            )
            with runs.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            d = row["diagnostics"]
            print(case["case_id"], d["stage"], d["hypothesis"], "downgraded", d["downgraded"],
                  "hints", d["forbidden_claim_hints"], flush=True)
    finally:
        knowledge.close()
    rows = [json.loads(line) for line in runs.read_text(encoding="utf-8").splitlines() if line.strip()]
    usage = [r["diagnostics"]["usage"] for r in rows]
    summary = dict(
        model=os.getenv("LLM_MODEL"),
        cases=len(rows),
        completed=sum(r["diagnostics"]["stage"] == "COMPLETED" for r in rows),
        downgraded_claims=sum(r["diagnostics"]["downgraded"] for r in rows),
        cases_with_forbidden_hints=[r["case_id"] for r in rows if r["diagnostics"]["forbidden_claim_hints"]],
        llm_calls=sum(u["llm_calls"] for u in usage),
        prompt_tokens=sum(u["prompt_tokens"] for u in usage),
        completion_tokens=sum(u["completion_tokens"] for u in usage),
        usage_complete=all(u["complete"] for u in usage),
        cases_with_usage_anomalies=[r["case_id"] for r in rows if r["diagnostics"]["usage_anomalies"]],
        semantic_review="not performed by this script",
    )
    (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
