"""Explicit opt-in live Agent evaluation or network-free replay/review."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path

from evaluation.agent.judges import validate_reviews
from evaluation.agent.metrics import summarize
from evaluation.agent.runner import RecordingLLM, load_cases, run_case
from evaluation.rag.provenance import code_state
from evaluation.rag.migration import protected_state

ROOT = Path(__file__).resolve().parents[2]


def write_reports(output, rows, metadata, reviews=None, input_price=None, output_price=None):
    summary = summarize(rows, reviews, input_price=input_price, output_price=output_price)
    for name, value in (("metadata", metadata), ("summary", summary), ("reviews", reviews or {})):
        (output / (name + ".json")).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    lines = ["# Agent development evaluation", "", "Execution/schema success is not semantic answer accuracy.",
             "Case labels and AI reviews remain provisional; no human approval is implied.", "",
             f"Cases: {summary['cases']}; execution OK: {summary['execution_ok']}; reviewed: {summary['reviewed_cases']}", ""]
    for row in rows:
        lines += ["## " + row["case_id"], "", "### Actual output", "```json", json.dumps(row["result"], ensure_ascii=False, indent=2),
                  "```", "", "### Expected boundaries (not sent to LLM)", json.dumps(row["expected"], ensure_ascii=False),
                  "", "### Error", json.dumps(row["error"], ensure_ascii=False), ""]
    (output / "review.md").write_text("\n".join(lines), encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=ROOT / "tests/agent_evaluation/cases.jsonl")
    parser.add_argument("--storage-dir", type=Path)
    parser.add_argument("--knowledge-dir", type=Path, default=ROOT / "app/knowledge")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--case-ids", help="Comma-separated subset; unknown IDs are rejected")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--max-calls", type=int, default=8)
    parser.add_argument("--max-input-chars", type=int, default=60000)
    parser.add_argument("--max-completion-tokens", type=int, default=4096)
    parser.add_argument("--timeout", type=float, default=90)
    parser.add_argument("--live", action="store_true", help="Explicitly permit paid requests with configured main LLM")
    parser.add_argument("--replay", type=Path, help="Existing results.jsonl: no model loading or network calls")
    parser.add_argument("--reviews", type=Path)
    parser.add_argument("--input-price-per-million", type=float)
    parser.add_argument("--output-price-per-million", type=float)
    args = parser.parse_args()
    if min(args.limit, args.max_calls, args.max_input_chars, args.max_completion_tokens, args.timeout) <= 0:
        parser.error("limits must be positive")
    if any(p is not None and (not math.isfinite(p) or p < 0) for p in (args.input_price_per_million, args.output_price_per_million)):
        parser.error("prices must be finite and nonnegative")
    if args.live == bool(args.replay):
        parser.error("choose exactly one of --live and --replay; no implicit paid calls")
    if args.live and args.storage_dir is None:
        parser.error("live evaluation requires explicit isolated --storage-dir")
    production = (ROOT / "app/storage").resolve()
    output = args.output_dir.resolve()
    for path in (args.storage_dir, output):
        if path is not None and (path.resolve() == production or path.resolve().is_relative_to(production)
                                 or production.is_relative_to(path.resolve())):
            parser.error("evaluation paths must not overlap production storage")
    cases, rows = [], []
    if args.replay:
        rows = [json.loads(line) for line in args.replay.read_text(encoding="utf-8").splitlines() if line.strip()]
        ids = [row["case_id"] for row in rows]
        if not ids or len(ids) != len(set(ids)):
            parser.error("replay requires nonempty, unique case IDs")
    else:
        cases = load_cases(args.cases)
        if args.case_ids:
            wanted = set(args.case_ids.split(","))
            if wanted - {c["case_id"] for c in cases}:
                parser.error("unknown case IDs")
            cases = [c for c in cases if c["case_id"] in wanted]
        cases = cases[:args.limit]
        ids = [case["case_id"] for case in cases]
    reviews = json.loads(args.reviews.read_text(encoding="utf-8")) if args.reviews else None
    validate_reviews(reviews or {}, ids)  # Reject bad review inputs before any paid request.
    output.mkdir(parents=True, exist_ok=False)
    metadata = {"cases_sha256": hashlib.sha256(args.cases.read_bytes()).hexdigest() if args.live else None, "live": args.live,
                "code": code_state(output), "limits": {"calls": args.max_calls, "input_chars": args.max_input_chars,
                "completion_tokens_per_request": args.max_completion_tokens, "timeout_seconds": args.timeout, "sdk_retries": 0}}
    protected_before = protected_state(production)
    if args.replay:
        metadata["replay_source_sha256"] = hashlib.sha256(args.replay.read_bytes()).hexdigest()
        # Preserve the real originating model/run metadata instead of attributing old outputs to current code.
        original = args.replay.parent / "metadata.json"
        metadata["origin"] = json.loads(original.read_text(encoding="utf-8")) if original.exists() else None
    else:
        os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", TOKENIZERS_PARALLELISM="false")
        from app.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
        from app.llm.client import LLMClient
        from app.rag.retriever import KnowledgeRetriever
        from app.rag.retrieval.policy import RetrievalPolicy
        client = LLMClient(LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, timeout=args.timeout, max_retries=0,
                           max_completion_tokens=args.max_completion_tokens)
        retriever = KnowledgeRetriever(knowledge_dir=args.knowledge_dir, storage_dir=args.storage_dir,
                                       retrieval_policy=RetrievalPolicy(default_strategy="hybrid"))
        llm = RecordingLLM(client, max_calls=args.max_calls, max_input_chars=args.max_input_chars)
        metadata.update(model=LLM_MODEL, embedding_model=retriever.model_name, index_generation=retriever._generation_id,
                        knowledge_dir=str(args.knowledge_dir.resolve()), storage_dir=str(args.storage_dir.resolve()))
        (output / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        with (output / "results.jsonl").open("w", encoding="utf-8") as stream:
            for case in cases:
                if llm.attempts >= llm.max_calls:
                    metadata["stopped_reason"] = "request_budget_exhausted"
                    break
                row = run_case(case, retriever, llm)
                rows.append(row)
                stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
                stream.flush()
                print(case["case_id"], "OK" if row["error"] is None else row["error"]["type"], flush=True)
                if row["error"] and row["error"]["type"] in {"LLMRequestError", "LLMConfigurationError", "EvaluationBudgetError"}:
                    metadata["stopped_reason"] = row["error"]["type"]
                    break
    if args.replay:
        (output / "results.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    metadata["selected_cases"] = ids
    metadata["completed_cases"] = [row["case_id"] for row in rows]
    metadata["production_unchanged"] = protected_before == protected_state(production)
    summary = write_reports(output, rows, metadata, reviews, args.input_price_per_million, args.output_price_per_million)
    print(json.dumps({"cases": len(rows), "execution_ok": summary["execution_ok"], "output": str(output)}), flush=True)
    success = (rows and summary["execution_ok"] == summary["schema_ok"] == len(rows)
               and not summary["semantic_fail_cases"] and metadata["production_unchanged"]
               and (args.replay or len(rows) == len(cases)))
    return 0 if success else 1
