"""Investigate alerts from a JSON file: python -m agent <alerts.json> [--alert-id ID]

Needs LLM_API_KEY / LLM_BASE_URL / LLM_MODEL for the model, and RAG_SERVICE_URL /
RAG_SERVICE_TOKEN (a scoped read-only key) / RAG_SERVICE_KNOWLEDGE_BASES for the
knowledge service. Each alert costs at most Budget.max_llm_calls model requests.
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("alerts", type=Path, help="JSON list of alerts (the batch)")
    parser.add_argument("--alert-id", help="Investigate one alert; default: all")
    parser.add_argument("--output", type=Path, help="Write results here (JSON)")
    parser.add_argument("--max-alerts", type=int, default=5, help="Cost guard")
    parser.add_argument("--language", help="Report language; default follows the alert")
    args = parser.parse_args()

    from agent.investigator import Investigator
    from agent.knowledge import RAGKnowledge
    from app.models.llm.client import LLMClient

    pool = json.loads(args.alerts.read_text(encoding="utf-8"))
    targets = [a for a in pool if args.alert_id in (None, a.get("id"))]
    if not targets:
        parser.error("No alert with that id")
    if len(targets) > args.max_alerts:
        parser.error(f"{len(targets)} alerts exceed --max-alerts {args.max_alerts}")
    llm = LLMClient(
        os.getenv("LLM_API_KEY"), os.getenv("LLM_BASE_URL"), os.getenv("LLM_MODEL"),
        timeout=float(os.getenv("AGENT_LLM_TIMEOUT", "90")), max_retries=1,
        max_completion_tokens=int(os.getenv("AGENT_MAX_COMPLETION_TOKENS", "4096")),
    )
    knowledge = RAGKnowledge()
    try:
        investigator = Investigator(llm, knowledge, language=args.language)
        results = [investigator.investigate(a, pool) for a in targets]
    finally:
        knowledge.close()
    text = json.dumps(results, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    for result in results:
        report = result["report"] or {}
        hypothesis = report.get("attack_hypothesis", {})
        print(
            f"{result['alert_id']}: {result['stage']} | {hypothesis.get('label')} "
            f"({hypothesis.get('status')}, {hypothesis.get('confidence')}) | "
            f"downgraded={len(report.get('verification', {}).get('downgraded', []))} | "
            f"llm_calls={result['usage']['llm_calls']} tokens="
            f"{result['usage']['prompt_tokens']}+{result['usage']['completion_tokens']}"
            + (f" | {result['failure']}" if result["failure"] else ""),
            file=sys.stderr,
        )
    if not args.output:
        print(text)


if __name__ == "__main__":
    main()
