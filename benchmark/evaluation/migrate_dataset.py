"""Materialize the versioned benchmark contract from the legacy candidate files."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .contract import (
    CONTRACT_VERSION,
    load_jsonl,
    normalize_agent_case,
    normalize_question,
    validate_items,
    write_jsonl,
)


def migrate_questions(path: Path, manifest: dict) -> list[dict]:
    return [normalize_question(row, manifest) for row in load_jsonl(path)]


def migrate_cases(path: Path, manifest: dict, question_families: dict[str, str]) -> list[dict]:
    return [normalize_agent_case(row, manifest, question_families) for row in load_jsonl(path)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--questions", type=Path, default=root / "datasets/security-v1-r3/dataset/questions.jsonl")
    parser.add_argument("--cases", type=Path, default=root / "evaluation/agent/cases.jsonl")
    parser.add_argument("--in-place", action="store_true", help="overwrite the two candidate files")
    args = parser.parse_args(argv)
    if not args.in_place:
        parser.error("migration is explicit: pass --in-place")
    benchmark = root / "datasets/security-v1-r3"
    manifest = json.loads((benchmark / "manifest.json").read_text(encoding="utf-8"))
    questions = migrate_questions(args.questions, manifest)
    question_families = {row["id"]: row["query_family"] for row in questions}
    cases = migrate_cases(args.cases, manifest, question_families)
    for item in questions + cases:
        item["machine_status"] = "pending_validation"
    write_jsonl(args.questions, questions)
    write_jsonl(args.cases, cases)
    dataset_meta_path = args.questions.parent / "dataset.json"
    dataset_meta = json.loads(dataset_meta_path.read_text(encoding="utf-8"))
    dataset_meta["data_contract_version"] = CONTRACT_VERSION
    dataset_meta["version"] = "security-rag-benchmark-v1-100-candidate-r3"
    dataset_meta["split"] = {"algorithm": "sha256-family-preserved-holdout-two-stage-v1", "salt": "security-v1-family-split-v1", "preserved_holdout": "sha256(holdout-v1:<query_family>) mod 5 == 0", "remaining_partition": "sha256(development-v1:<query_family>) mod 2; 40% development / 40% regression / 20% final_holdout"}
    dataset_meta["questions_sha256"] = hashlib.sha256(args.questions.read_bytes()).hexdigest()
    dataset_meta["annotation_notice"] = "Candidate labels are not human-reviewed; deterministic validation checks integrity only; semantic review is opt-in and machine-generated."
    dataset_meta["machine_validation"] = {"validator_version": "deterministic-contract-checker-v1", "status": "pending_validation", "unresolved": None, "human_reviewed": 0, "semantic_review": "not_run"}
    dataset_meta_path.write_text(json.dumps(dataset_meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_path = benchmark / "manifest.json"
    manifest["dataset_files"] = manifest.get("dataset_files", [])
    for entry in manifest["dataset_files"]:
        candidate = (benchmark / entry["file"]).resolve()
        if candidate.is_file():
            entry["sha256"] = hashlib.sha256(candidate.read_bytes()).hexdigest()
            entry["items"] = len(load_jsonl(candidate))
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"contract_version": CONTRACT_VERSION, "questions": len(questions), "cases": len(cases)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
