"""Reproducible, isolated legacy-to-managed migration acceptance; never switch production."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

from evaluation.rag.provenance import code_state

ROOT = Path(__file__).resolve().parents[2]


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def compare_runs(before, after):
    old = {row["id"]: row["results"] for row in before["served"]}
    new = {row["id"]: row["results"] for row in after["served"]}
    differences = [key for key in sorted(old.keys() | new.keys()) if old.get(key) != new.get(key)]
    regressions, errors = [], []
    old_rows = {row["question_id"]: row for row in before["benchmark"]}
    new_rows = {row["question_id"]: row for row in after["benchmark"]}
    if old_rows.keys() != new_rows.keys():
        errors.append("benchmark question sets differ")
    for key, row in new_rows.items():
        if row["error"]:
            errors.append(key)
        prior = old_rows.get(key)
        if prior is None:
            continue
        if prior["error"]:
            errors.append("baseline:" + key)
        for k, metrics in row["metrics_by_k"].items():
            for unit in ("child", "parent"):
                for metric, value in metrics[unit].items():
                    previous = prior["metrics_by_k"][k][unit][metric]
                    if value is not None and previous is not None and value + 1e-9 < previous:
                        regressions.append(dict(question_id=key, k=k, unit=unit, metric=metric,
                                                before=previous, after=value))
    checks = {"same_indexed_content": before["units_fingerprint"] == after["units_fingerprint"],
              "same_counts": before["counts"] == after["counts"],
              "same_online_evidence_order": not differences,
              "no_metric_regression": not regressions, "no_query_errors": not errors}
    recovery = after.get("recovery", {})
    checks.update({"recovery:" + k: v for k, v in recovery.items() if isinstance(v, bool)})
    return {"passed": all(checks.values()), "checks": checks, "changed_queries": differences,
            "metric_regressions": regressions, "query_errors": errors}


def protected_state(storage):
    paths = list((storage / "indexes").rglob("*")) + list(storage.glob("registry.db*"))
    return {str(p.relative_to(storage)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths) if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ref", required=True, help="Explicit known-good legacy Git revision")
    parser.add_argument("--output-dir", type=Path, required=True, help="New disposable directory, never app/storage")
    parser.add_argument("--dataset", type=Path, help="Optional explicit benchmark; omitted by default")
    parser.add_argument("--knowledge-dir", type=Path, default=ROOT / "app/knowledge")
    parser.add_argument("--model", default="BAAI/bge-m3")
    parser.add_argument("--worker-timeout", type=float, default=1800)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    production = ROOT / "app/storage"
    protected = [production, args.knowledge_dir.resolve()]
    if args.dataset is not None:
        protected.append(args.dataset.resolve().parent)
    if any(output == path or output.is_relative_to(path) or path.is_relative_to(output) for path in protected):
        parser.error("output directory must not overlap production storage, knowledge or annotations")
    if args.worker_timeout <= 0:
        parser.error("worker timeout must be positive")
    revision = subprocess.check_output(["git", "rev-parse", "--verify", args.baseline_ref + "^{commit}"], cwd=ROOT).decode().strip()
    output.mkdir(parents=True, exist_ok=False)
    initial = protected_state(production)
    write_json(output / "production_before.json", initial)
    code = output / "legacy-code"
    archive = subprocess.check_output(["git", "archive", "--format=zip", revision], cwd=ROOT)
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        bundle.extractall(code)
    cases = [json.loads(line) for line in (ROOT / "tests/agent_evaluation/cases.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    queries = output / "production_queries.json"
    write_json(queries, [{"id": case["case_id"], "query": case["alert"]["title"] + " " + case["alert"]["description"]} for case in cases])
    profiles = [("production", args.knowledge_dir.resolve(), None)]
    if args.dataset is not None:
        metadata = json.loads((args.dataset.parent / "dataset.json").read_text(encoding="utf-8"))
        corpus = (args.dataset.parent / metadata["documents_dir"]).resolve()
        profiles.append(("benchmark", corpus, args.dataset.resolve()))
    summary = {"baseline_commit": revision,
               "candidate_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
               "model": args.model, "production_switched": False, "profiles": {}, "candidate_code": code_state(output),
               "dataset_sha256": hashlib.sha256(args.dataset.read_bytes()).hexdigest() if args.dataset else None,
               "candidate_changes": subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=ROOT).decode().splitlines()}
    worker = Path(__file__).with_name("acceptance_worker.py")
    def run(label, code_root, storage, knowledge, report, dataset=None, drill=False, load_only=False):
        cmd = [sys.executable, str(worker), "--code-root", str(code_root), "--storage-dir", str(storage),
               "--knowledge-dir", str(knowledge), "--model", args.model, "--output", str(report)]
        cmd += ["--dataset", str(dataset)] if dataset else ["--queries", str(queries)]
        if drill:
            cmd.append("--exercise")
        if load_only:
            cmd.append("--load-only")
        print(label, flush=True)
        with (output / (label + ".log")).open("w", encoding="utf-8") as log:
            subprocess.run(cmd, cwd=code_root, stdout=log, stderr=subprocess.STDOUT, check=True,
                           timeout=args.worker_timeout, env=dict(os.environ, PYTHONUTF8="1"))
        return json.loads(report.read_text(encoding="utf-8"))
    try:
        for profile, knowledge, dataset in profiles:
            folder = output / profile
            folder.mkdir()
            old_storage, new_storage = folder / "legacy-storage", folder / "managed-storage"
            before = run(profile + "_legacy", code, old_storage, knowledge, folder / "before.json", dataset)
            # Whole legacy storage/code remain available for old-format rollback.
            shutil.copytree(old_storage, new_storage)
            after = run(profile + "_managed", ROOT, new_storage, knowledge, folder / "after.json", dataset, drill=True)
            comparison = compare_runs(before, after)
            restored = run(profile + "_legacy_restore", code, old_storage, knowledge, folder / "restored.json", dataset, load_only=True)
            comparison["checks"]["legacy_backup_replay"] = (before["served"] == restored["served"] and
                                                               before["generation"] == restored["generation"])
            comparison["passed"] = all(comparison["checks"].values())
            summary["profiles"][profile] = comparison
            write_json(folder / "comparison.json", comparison)
            write_json(output / "summary.json", summary)
    finally:
        final = protected_state(production)
        write_json(output / "production_after.json", final)
        summary["production_unchanged"] = initial == final
        summary["passed"] = (len(summary["profiles"]) == len(profiles) and all(p["passed"] for p in summary["profiles"].values()) and initial == final)
        write_json(output / "summary.json", summary)
    print(json.dumps({"passed": summary["passed"], "report": str(output / "summary.json")}), flush=True)
    return 0 if summary["passed"] else 1
