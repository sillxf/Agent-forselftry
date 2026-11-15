"""Offline validation for benchmark contracts, provenance, and family splits."""
from __future__ import annotations

import argparse
import json
import hashlib
from pathlib import Path

from .contract import load_jsonl, normalize_agent_case, normalize_question, validate_items


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    root = Path(__file__).resolve().parents[1]
    benchmark = root / "datasets/security-v1-r3"
    parser.add_argument("--questions", type=Path, default=benchmark / "dataset/questions.jsonl")
    parser.add_argument("--cases", type=Path, default=Path(__file__).resolve().parent / "agent/cases.jsonl")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--legacy-ok", action="store_true", help="normalize legacy rows in memory before checking")
    parser.add_argument("--write-status", action="store_true", help="materialize deterministic machine_status and machine_review into input JSONL")
    args = parser.parse_args(argv)
    manifest = json.loads((benchmark / "manifest.json").read_text(encoding="utf-8"))
    reports = {}
    loaded = {}
    converters = {}
    for name, path, converter in (
        ("questions", args.questions, normalize_question),
        ("agent_cases", args.cases, normalize_agent_case),
    ):
        rows = load_jsonl(path)
        if args.legacy_ok:
            rows = [converter(row, manifest) for row in rows]
        loaded[name] = rows
        converters[name] = (path, converter)
        reports[name] = validate_items(rows, benchmark, manifest, require_contract=not args.legacy_ok)
    input_file_checks = []
    for entry in manifest.get("dataset_files", []):
        candidate = (benchmark / entry.get("file", "")).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            input_file_checks.append({"file": entry.get("file"), "valid": False, "issue": "path_outside_benchmark_workspace"})
            continue
        if not candidate.is_file():
            input_file_checks.append({"file": entry.get("file"), "valid": False, "issue": "missing_file"})
            continue
        actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
        expected = entry.get("sha256")
        row = {"file": entry.get("file"), "valid": actual == expected, "expected_sha256": expected, "actual_sha256": actual}
        if candidate.suffix == ".jsonl":
            row["items"] = len(load_jsonl(candidate))
            row["expected_items"] = entry.get("items")
            row["valid"] = row["valid"] and row["items"] == row["expected_items"]
        if not row["valid"]:
            row["issue"] = "hash_or_item_count_mismatch"
        input_file_checks.append(row)
    report = {"valid": all(value["valid"] for value in reports.values()) and all(row["valid"] for row in input_file_checks), "datasets": reports, "input_file_hashes": input_file_checks}
    if args.write_status:
        for name, rows in loaded.items():
            status_report = reports[name]
            issue_map = {}
            for issue in status_report["issues"]:
                issue_map.setdefault(issue["id"], []).append(issue["code"])
            for row in rows:
                item_id = row.get("id") or row.get("case_id")
                row["machine_status"] = status_report["status_by_id"].get(item_id, "unresolved")
                row["machine_review"] = {"reviewer": "deterministic-contract-checker-v1", "status": "not_run", "integrity_status": row["machine_status"], "confidence": None, "uncertainty_reasons": sorted(set(issue_map.get(item_id, []))) or ["semantic_review_not_run"], "human_reviewed": False}
            path, _ = converters[name]
            path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    target = args.report or (root / "runs/quality-validation/validation.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
