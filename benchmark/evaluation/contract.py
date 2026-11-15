"""Versioned benchmark contract, deterministic provenance checks, and stable splits.

This module intentionally has no model/network dependency. It is the offline boundary
for candidate data: source hashes, evidence anchors, field contracts, and family-level
split leakage are checked before any paid or semantic review is considered.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree

CONTRACT_VERSION = "security-benchmark-item-v1"
SPLIT_ALGORITHM = "sha256-family-preserved-holdout-two-stage-v1"
SPLIT_SALT = "security-v1-family-split-v1"
SPLIT_THRESHOLDS = ((40, "development"), (80, "regression"), (100, "final_holdout"))
MACHINE_STATUSES = {"pending_validation", "machine_validated", "unresolved"}
ANSWERABILITY = {"answerable", "unanswerable", "unknown"}
SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_ -]?key|token|password|secret)\s*[:=]\s*[^\s,;]+"),
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
)


@dataclass(frozen=True)
class ValidationIssue:
    item_id: str
    code: str
    message: str
    severity: str = "error"

    def as_dict(self) -> dict[str, str]:
        return {"id": self.item_id, "code": self.code, "message": self.message, "severity": self.severity}


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_no}: expected JSON object")
        rows.append(row)
    return rows


def write_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> None:
    Path(path).write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stable_split(query_family: str, *, salt: str = SPLIT_SALT) -> str:
    """Assign a complete query family to exactly one reproducible split."""
    # Preserve the prior holdout-v1 20% family assignment exactly. Partition the
    # remaining families evenly into development and regression without touching it.
    if salt == SPLIT_SALT:
        held_out = int(hashlib.sha256(("holdout-v1:" + query_family).encode("utf-8")).hexdigest(), 16) % 5 == 0
        if held_out:
            return "final_holdout"
        dev = int(hashlib.sha256(("development-v1:" + query_family).encode("utf-8")).hexdigest(), 16) % 2 == 0
        return "development" if dev else "regression"
    bucket = int(hashlib.sha256(f"{salt}:{query_family}".encode("utf-8")).hexdigest(), 16) % 100
    for limit, name in SPLIT_THRESHOLDS:
        if bucket < limit:
            return name
    raise AssertionError("unreachable split bucket")


def _manifest_by_file(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["file"]: entry for entry in manifest.get("documents", []) if isinstance(entry, dict) and entry.get("file")}


def _legacy_evidence(row: dict[str, Any], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    by_file = _manifest_by_file(manifest)
    out: list[dict[str, Any]] = []
    for evidence in row.get("relevant_evidence", []):
        item = dict(evidence)
        entry = by_file.get(item.get("source"), {})
        item["source_sha256"] = entry.get("sha256", item.get("document_id", ""))
        item.setdefault("anchors", [{"kind": "quote", "text": item.get("text_quote", "")}])
        out.append(item)
        for alt_index, alternative in enumerate(item.get("alternatives", []), 1):
            alt = dict(alternative)
            alt["evidence_id"] = f"{item.get('evidence_id', 'evidence')}:alternative:{alt_index}"
            alt["source_sha256"] = by_file.get(alt.get("source"), {}).get("sha256", alt.get("document_id", ""))
            alt.setdefault("anchors", [{"kind": "quote", "text": alt.get("text_quote", "")}])
            out.append(alt)
    return out


def normalize_question(row: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    """Add v1 contract fields without discarding the historical candidate fields."""
    item = dict(row)
    evidence = _legacy_evidence(row, manifest)
    answerability = "answerable" if row.get("answerable") is True else "unanswerable" if row.get("answerable") is False else "unknown"
    facts = []
    if answerability == "answerable":
        for evidence_item in row.get("relevant_evidence", []):
            quote = evidence_item.get("text_quote", "")
            facts.append(
                {
                    "fact_id": evidence_item.get("evidence_id"),
                    "statement": quote,
                    "evidence_ids": [evidence_item.get("evidence_id")],
                    "accepted_alternatives": [quote, *[a.get("text_quote", "") for a in evidence_item.get("alternatives", [])]],
                    "label_basis": "legacy_relevant_evidence",
                }
            )
    family = row.get("query_family") or row["id"]
    item.update(
        {
            "contract_version": CONTRACT_VERSION,
            "task": {"kind": "rag_question", "prompt": row.get("question", "")},
            "answerability": answerability,
            "source_evidence": evidence,
            "required_facts": facts,
            "acceptable_alternatives": [row["expected_answer"]] if row.get("expected_answer") and answerability == "answerable" else [],
            "prohibited_conclusions": list(row.get("must_not_include", row.get("forbidden_conclusions", [])) or []),
            "expected_tool_behavior": row.get("expected_tool_behavior")
            or {"retrieval_required": True, "citation_required": answerability == "answerable", "refuse_if_unanswerable": answerability == "unanswerable"},
            "query_family": family,
            "split": row.get("split") or stable_split(family),
            "annotation_provenance": {
                "origin": row.get("annotation_provenance", {}).get("origin", "legacy_candidate"),
                "human_reviewed": False,
                "original_review_status": row.get("review_status", "pending"),
            },
            "machine_status": row.get("machine_status", "pending_validation"),
            "machine_review": row.get("machine_review", {"reviewer": "deterministic-contract-checker-v1"}),
        }
    )
    return item


def normalize_agent_case(row: dict[str, Any], manifest: dict[str, Any], question_families: dict[str, str] | None = None) -> dict[str, Any]:
    item = dict(row)
    item.setdefault("id", row.get("case_id"))
    reference = row.get("reference_knowledge") or {}
    evidence = []
    for ev in reference.get("evidence", []):
        copy = dict(ev)
        copy["source_sha256"] = _manifest_by_file(manifest).get(copy.get("source"), {}).get("sha256", copy.get("document_id", ""))
        copy.setdefault("anchors", [{"kind": "quote", "text": copy.get("text_quote", "")}])
        evidence.append(copy)
    linked_question = row.get("knowledge_gap_question_id") or reference.get("benchmark_question_id")
    family = row.get("query_family") or ((question_families or {}).get(linked_question) if linked_question else None) or ("agent:" + row["case_id"])
    item.update(
        {
            "contract_version": CONTRACT_VERSION,
            "task": {"kind": "agent_investigation", "prompt": row.get("expected_behavior", "")},
            "answerability": "answerable" if evidence or row.get("observed_event") else "unknown",
            "source_evidence": evidence,
            "required_facts": [
                *[ {"fact_id": f"observed-{index + 1}", "statement": statement, "evidence_ids": [], "label_basis": "synthetic_alert_observation"} for index, statement in enumerate(row.get("observed_event", [])) ],
                *[ {"fact_id": ev.get("evidence_id"), "statement": ev.get("text_quote", ""), "evidence_ids": [ev.get("evidence_id")], "label_basis": "synthetic_reference_knowledge"} for ev in evidence ],
            ],
            "acceptable_alternatives": [],
            "prohibited_conclusions": list(row.get("forbidden_claims", [])),
            "expected_tool_behavior": {
                "retrieval_required": bool(reference),
                "preserve_observed_vs_reference": True,
                "resist_prompt_injection": "injection" in row.get("expected_behavior", "").casefold(),
            },
            "difficulty": row.get("difficulty", "medium"),
            "category": row.get("category", "agent_safety"),
            "query_family": family,
            "split": row.get("split") or stable_split(family),
            "annotation_provenance": {"origin": "synthetic_design_case", "human_reviewed": False, "original_review_status": row.get("review_status", "pending")},
            "machine_status": row.get("machine_status", "pending_validation"),
            "machine_review": row.get("machine_review", {"reviewer": "deterministic-contract-checker-v1"}),
        }
    )
    return item


def _text_for_source(path: Path) -> list[tuple[int | None, str]] | None:
    suffix = path.suffix.casefold()
    if suffix in {".md", ".markdown", ".txt", ".json", ".csv"}:
        return [(None, path.read_text(encoding="utf-8", errors="replace"))]
    if suffix == ".docx":
        try:
            with zipfile.ZipFile(path) as archive:
                xml = archive.read("word/document.xml")
            root = ElementTree.fromstring(xml)
            texts = [node.text or "" for node in root.iter() if node.tag.endswith("}t")]
            return [(None, " ".join(texts))]
        except Exception:
            return None
    if suffix == ".pdf":
        try:
            import pypdfium2
            document = pypdfium2.PdfDocument(str(path))
            pages = []
            for number, page in enumerate(document, 1):
                page_text = page.get_textpage().get_text_range()
                pages.append((number, page_text))
                page.close()
            return pages
        except Exception:
            return None
    return None


def _quote_found(quote: str, page_text: str) -> bool:
    if not quote:
        return False
    direct = quote in page_text
    compact = " ".join(quote.split())
    normalized = " ".join(page_text.split())
    return direct or (compact and compact in normalized)


def _validate_evidence(item_id: str, evidence: dict[str, Any], benchmark_dir: Path, manifest_by_file: dict[str, dict[str, Any]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    source = evidence.get("source")
    if not isinstance(source, str):
        return [ValidationIssue(item_id, "evidence_source_type", "evidence source must be a string")]
    entry = manifest_by_file.get(source)
    if not source or not entry:
        return [ValidationIssue(item_id, "unknown_source", f"evidence source is not in manifest: {source!r}")]
    path = benchmark_dir / "documents" / source
    if not path.is_file():
        return [ValidationIssue(item_id, "missing_source_file", f"source file does not exist: {source}")]
    actual = sha256_file(path)
    if actual != entry.get("sha256"):
        issues.append(ValidationIssue(item_id, "source_hash_mismatch", f"manifest hash mismatch for {source}"))
    if evidence.get("source_sha256") and evidence["source_sha256"] != actual:
        issues.append(ValidationIssue(item_id, "evidence_hash_mismatch", f"evidence hash mismatch for {source}"))
    if not evidence.get("evidence_id") or not evidence.get("source_block_ids"):
        issues.append(ValidationIssue(item_id, "invalid_anchor_shape", f"evidence {evidence.get('evidence_id')} needs evidence_id and source_block_ids"))
    texts = _text_for_source(path)
    if texts is None:
        issues.append(ValidationIssue(item_id, "unresolved_anchor", f"could not extract text for {source}", "warning"))
    else:
        anchors = evidence.get("anchors") or [{"kind": "quote", "text": evidence.get("text_quote", ""), "page_number": evidence.get("page_number")}]
        if not isinstance(anchors, list):
            issues.append(ValidationIssue(item_id, "anchor_type", "evidence anchors must be an array"))
            anchors = []
        for anchor in anchors:
            if not isinstance(anchor, dict):
                issues.append(ValidationIssue(item_id, "anchor_type", "evidence anchors must contain objects"))
                continue
            quote = anchor.get("text", "")
            page_hint = anchor.get("page_number")
            candidates = [text for page, text in texts if page_hint is None or page == page_hint]
            # PDF table extraction can linearize cells differently; the explicit
            # page/block anchor remains the provenance record even when its text
            # is normalized by the parser.
            if not any(_quote_found(quote, text) for text in candidates):
                candidates = [text for _, text in texts]
            if not any(_quote_found(quote, text) for text in candidates):
                issues.append(ValidationIssue(item_id, "invalid_evidence_anchor", f"quote not found in {source}: {quote[:100]!r}"))
    return issues


def _schema_type_matches(value: Any, expected: str) -> bool:
    checks = {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
        "null": lambda v: v is None,
    }
    return checks.get(expected, lambda _: True)(value)


def _schema_issues(value: Any, schema: dict[str, Any], *, root_schema: dict[str, Any], path: str = "$", item_id: str) -> list[ValidationIssue]:
    """Validate the JSON Schema subset used by the checked-in v1 schema.

    Keeping this dependency-free makes integrity checks usable in offline installs.
    The schema is loaded from the manifest on every validation run.
    """
    issues: list[ValidationIssue] = []
    ref = schema.get("$ref")
    if ref:
        if not ref.startswith("#/"):
            return [ValidationIssue(item_id, "schema_ref_unsupported", f"unsupported schema ref at {path}")]
        target: Any = root_schema
        try:
            for component in ref[2:].split("/"):
                target = target[component.replace("~1", "/").replace("~0", "~")]
        except (KeyError, TypeError):
            return [ValidationIssue(item_id, "schema_ref_invalid", f"unresolvable schema ref at {path}")]
        return _schema_issues(value, target, root_schema=root_schema, path=path, item_id=item_id)

    expected_types = schema.get("type")
    if expected_types is not None:
        allowed = expected_types if isinstance(expected_types, list) else [expected_types]
        if not any(_schema_type_matches(value, kind) for kind in allowed):
            return [ValidationIssue(item_id, "schema_type", f"{path} must have type {'|'.join(allowed)}")]
    if "const" in schema and value != schema["const"]:
        issues.append(ValidationIssue(item_id, "schema_const", f"{path} must equal its declared constant"))
    if "enum" in schema and value not in schema["enum"]:
        issues.append(ValidationIssue(item_id, "schema_enum", f"{path} is outside its declared enum"))
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            issues.append(ValidationIssue(item_id, "schema_min_length", f"{path} is shorter than minLength"))
        pattern = schema.get("pattern")
        if pattern and re.search(pattern, value) is None:
            issues.append(ValidationIssue(item_id, "schema_pattern", f"{path} does not match its declared pattern"))
    if isinstance(value, (int, float)) and not isinstance(value, bool) and "minimum" in schema and value < schema["minimum"]:
        issues.append(ValidationIssue(item_id, "schema_minimum", f"{path} is below its declared minimum"))
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            issues.append(ValidationIssue(item_id, "schema_min_items", f"{path} has fewer than minItems"))
        if "items" in schema:
            for index, child in enumerate(value):
                issues.extend(_schema_issues(child, schema["items"], root_schema=root_schema, path=f"{path}[{index}]", item_id=item_id))
    if isinstance(value, dict):
        required = schema.get("required", [])
        for name in required:
            if name not in value:
                issues.append(ValidationIssue(item_id, "schema_required", f"{path}.{name} is required"))
        properties = schema.get("properties", {})
        for name, child in value.items():
            if name in properties:
                issues.extend(_schema_issues(child, properties[name], root_schema=root_schema, path=f"{path}.{name}", item_id=item_id))
            elif schema.get("additionalProperties") is False:
                issues.append(ValidationIssue(item_id, "schema_additional_property", f"{path}.{name} is not allowed"))
    return issues


def validate_items(items: list[dict[str, Any]], benchmark_dir: str | Path, manifest: dict[str, Any], *, require_contract: bool = True) -> dict[str, Any]:
    benchmark_dir = Path(benchmark_dir)
    issues: list[ValidationIssue] = []
    seen: set[str] = set()
    family_splits: dict[str, set[str]] = {}
    manifest_by_file = _manifest_by_file(manifest)
    schema = None
    schema_ref = (manifest.get("data_contract") or {}).get("schema") if isinstance(manifest.get("data_contract"), dict) else None
    schema_path = (benchmark_dir / schema_ref).resolve() if schema_ref else (Path(__file__).resolve().parent / "schemas/security-benchmark-item-v1.schema.json")
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(ValidationIssue("<schema>", "schema_load_error", f"could not load contract schema ({type(exc).__name__})"))
    item_ids = {str(item.get("id") or item.get("case_id") or "<missing>") for item in items if isinstance(item, dict)}
    family_members: dict[str, list[str]] = {}
    for candidate in items:
        if isinstance(candidate, dict) and candidate.get("query_family"):
            family_members.setdefault(candidate["query_family"], []).append(str(candidate.get("id") or candidate.get("case_id") or "<missing>"))
    for item in items:
        if not isinstance(item, dict):
            issues.append(ValidationIssue("<invalid-item>", "schema_type", "dataset entries must be JSON objects"))
            continue
        item_id = str(item.get("id") or item.get("case_id") or "<missing>")
        if schema is not None:
            issues.extend(_schema_issues(item, schema, root_schema=schema, item_id=item_id))
        if item_id in seen:
            issues.append(ValidationIssue(item_id, "duplicate_id", "item id is duplicated"))
        seen.add(item_id)
        required = {"contract_version", "task", "answerability", "source_evidence", "required_facts", "acceptable_alternatives", "prohibited_conclusions", "expected_tool_behavior", "difficulty", "category", "query_family", "split", "annotation_provenance", "machine_status", "machine_review", "review_status"}
        if require_contract:
            for name in sorted(required - item.keys()):
                issues.append(ValidationIssue(item_id, "missing_field", f"missing required field: {name}"))
        if item.get("contract_version") != CONTRACT_VERSION:
            issues.append(ValidationIssue(item_id, "contract_version", f"expected {CONTRACT_VERSION}"))
        if item.get("answerability") not in ANSWERABILITY:
            issues.append(ValidationIssue(item_id, "answerability", "must be answerable, unanswerable, or unknown"))
        if item.get("machine_status") not in MACHINE_STATUSES:
            issues.append(ValidationIssue(item_id, "machine_status", "invalid machine status"))
        provenance = item.get("annotation_provenance")
        if not isinstance(provenance, dict):
            issues.append(ValidationIssue(item_id, "annotation_provenance_type", "annotation_provenance must be an object"))
            provenance = {}
        if provenance.get("human_reviewed") is not False:
            issues.append(ValidationIssue(item_id, "human_review_claim", "candidate data must not claim human review"))
        family, split = item.get("query_family"), item.get("split")
        if isinstance(family, str) and isinstance(split, str) and family and split:
            family_splits.setdefault(family, set()).add(split)
        evidence = item.get("source_evidence")
        if not isinstance(evidence, list):
            issues.append(ValidationIssue(item_id, "evidence_type", "source_evidence must be an array"))
            evidence = []
        evidence_ids = [e.get("evidence_id") for e in evidence if isinstance(e, dict) and isinstance(e.get("evidence_id"), str)]
        if len(evidence_ids) != len(set(evidence_ids)):
            issues.append(ValidationIssue(item_id, "duplicate_evidence_id", "evidence ids must be unique within an item"))
        for ev in evidence:
            if isinstance(ev, dict):
                issues.extend(_validate_evidence(item_id, ev, benchmark_dir, manifest_by_file))
            else:
                issues.append(ValidationIssue(item_id, "evidence_type", "source_evidence entries must be objects"))
        facts = item.get("required_facts")
        if not isinstance(facts, list):
            issues.append(ValidationIssue(item_id, "fact_type", "required_facts must be an array"))
            facts = []
        task = item.get("task") if isinstance(item.get("task"), dict) else {}
        if item.get("answerability") == "answerable" and not evidence and task.get("kind") != "agent_investigation":
            issues.append(ValidationIssue(item_id, "answerable_without_evidence", "answerable item needs source evidence"))
        if item.get("answerability") == "unanswerable" and (evidence or facts):
            issues.append(ValidationIssue(item_id, "unanswerable_with_facts", "unanswerable item cannot carry required facts/evidence"))
        known_fact_evidence = set(evidence_ids)
        for fact in facts:
            if not isinstance(fact, dict) or not fact.get("fact_id") or not fact.get("statement"):
                issues.append(ValidationIssue(item_id, "fact_shape", "required facts need fact_id and statement"))
                continue
            fact_evidence_ids = fact.get("evidence_ids", [])
            if not isinstance(fact_evidence_ids, list):
                issues.append(ValidationIssue(item_id, "fact_evidence_type", "fact evidence_ids must be an array"))
                fact_evidence_ids = []
            fact_evidence_ids = {evidence_id for evidence_id in fact_evidence_ids if isinstance(evidence_id, str)}
            missing_evidence = fact_evidence_ids - known_fact_evidence
            if missing_evidence:
                issues.append(ValidationIssue(item_id, "fact_evidence_missing", f"fact references unknown evidence: {sorted(missing_evidence)}"))
        prohibited_values = item.get("prohibited_conclusions")
        alternatives_values = item.get("acceptable_alternatives")
        if not isinstance(prohibited_values, list):
            issues.append(ValidationIssue(item_id, "prohibited_conclusions_type", "prohibited_conclusions must be an array"))
            prohibited_values = []
        if not isinstance(alternatives_values, list):
            issues.append(ValidationIssue(item_id, "acceptable_alternatives_type", "acceptable_alternatives must be an array"))
            alternatives_values = []
        prohibited = {" ".join(str(x).casefold().split()) for x in prohibited_values}
        alternatives = {" ".join(str(x).casefold().split()) for x in alternatives_values}
        overlap = sorted(prohibited & alternatives)
        if overlap:
            issues.append(ValidationIssue(item_id, "required_forbidden_overlap", f"same phrase is both acceptable and prohibited: {overlap}"))
    for family, splits in family_splits.items():
        if len(splits) > 1:
            issues.append(ValidationIssue(family, "split_leakage", f"query family appears in multiple splits: {sorted(splits)}"))
    hard_errors = [issue for issue in issues if issue.severity == "error"]
    unresolved_ids = set(item_ids) if schema is None else set()
    for issue in issues:
        if issue.severity != "error":
            continue
        if issue.item_id in item_ids:
            unresolved_ids.add(issue.item_id)
        else:
            unresolved_ids.update(family_members.get(issue.item_id, []))
    unresolved = sorted(unresolved_ids)
    status_by_id = {item_id: ("unresolved" if item_id in unresolved_ids else "machine_validated") for item_id in seen}
    return {
        "valid": not hard_errors,
        "items": len(items),
        "unique_ids": len(seen),
        "machine_validated": sum(status == "machine_validated" for status in status_by_id.values()),
        "unresolved": len(unresolved),
        "status_by_id": status_by_id,
        "issues": [issue.as_dict() for issue in issues],
        "split_algorithm": SPLIT_ALGORITHM,
        "split_salt": SPLIT_SALT,
        "splits": {split: sum(1 for item in items if item.get("split") == split) for _, split in SPLIT_THRESHOLDS},
    }


def redact(text: str) -> str:
    result = text or ""
    for pattern in SECRET_PATTERNS:
        result = pattern.sub("[REDACTED]", result)
    return result


def git_revision(root: str | Path) -> str | None:
    try:
        value = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
        return value or None
    except (OSError, subprocess.CalledProcessError):
        return None


def run_metadata(*, dataset_path: str | Path, dataset_version: str, code_root: str | Path, prompt_version: str | None = None, models: list[str] | None = None, budget: dict[str, Any] | None = None, split: str | None = None) -> dict[str, Any]:
    return {
        "data_version": dataset_version,
        "data_sha256": sha256_file(dataset_path),
        "code_commit": git_revision(code_root),
        "evaluator_version": CONTRACT_VERSION,
        "prompt_version": prompt_version,
        "models": models or [],
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "budget": budget or {},
        "split": split or "all",
        "limitations": [
            "machine adjudication is not human ground truth",
            "candidate data is not a cryptographically hidden test set",
            "lexical checks are deterministic submetrics, not semantic correctness",
        ],
    }
