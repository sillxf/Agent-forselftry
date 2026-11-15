"""Offline contract and split integrity tests."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from benchmark.evaluation.contract import load_jsonl, stable_split, validate_items

ROOT = Path(__file__).resolve().parents[2]
BENCHMARK = ROOT / "benchmark/datasets/security-v1-r3"


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((BENCHMARK / "manifest.json").read_text(encoding="utf-8"))
        self.questions = load_jsonl(BENCHMARK / "dataset/questions.jsonl")

    def test_current_candidates_are_machine_validated_and_family_grouped(self):
        result = validate_items(self.questions, BENCHMARK, self.manifest)
        self.assertTrue(result["valid"], result["issues"])
        self.assertEqual(result["items"], 100)
        self.assertEqual(result["unresolved"], 0)
        self.assertEqual(result["machine_validated"], 100)
        families = {}
        for row in self.questions:
            families.setdefault(row["query_family"], set()).add(row["split"])
        self.assertTrue(all(len(splits) == 1 for splits in families.values()))
        self.assertEqual(stable_split("legacy-rag_001"), self.questions[0]["split"])

    def test_legacy_r2_freeze_and_contract_r3_are_separate_versions(self):
        legacy = json.loads((ROOT / "benchmark/datasets/security-v1/dataset/dataset.json").read_text(encoding="utf-8"))
        migrated = json.loads((BENCHMARK / "dataset/dataset.json").read_text(encoding="utf-8"))
        self.assertEqual(legacy["version"], "security-rag-benchmark-v1-100-candidate-r2")
        self.assertEqual(migrated["version"], "security-rag-benchmark-v1-100-candidate-r3")
        self.assertNotEqual(legacy["version"], migrated["version"])

    def test_invalid_provenance_type_returns_schema_issue_without_raising(self):
        malformed = deepcopy(self.questions[0])
        malformed["annotation_provenance"] = "not-an-object"
        result = validate_items([malformed], BENCHMARK, self.manifest)
        codes = {issue["code"] for issue in result["issues"]}
        self.assertIn("schema_type", codes)
        self.assertIn("annotation_provenance_type", codes)
        self.assertFalse(result["valid"])

    def test_duplicate_id_hash_anchor_and_split_leakage_are_errors(self):
        duplicate = deepcopy(self.questions[0])
        rows = [self.questions[0], duplicate]
        result = validate_items(rows, BENCHMARK, self.manifest)
        self.assertIn("duplicate_id", {i["code"] for i in result["issues"]})

        bad_hash = deepcopy(self.questions[0])
        bad_hash["source_evidence"][0]["source_sha256"] = "0" * 64
        result = validate_items([bad_hash], BENCHMARK, self.manifest)
        self.assertIn("evidence_hash_mismatch", {i["code"] for i in result["issues"]})

        bad_anchor = deepcopy(self.questions[0])
        bad_anchor["source_evidence"][0]["anchors"] = [{"kind": "quote", "text": "not in frozen source"}]
        result = validate_items([bad_anchor], BENCHMARK, self.manifest)
        self.assertIn("invalid_evidence_anchor", {i["code"] for i in result["issues"]})

        leaked = deepcopy(self.questions[1])
        leaked["split"] = "development" if leaked["split"] != "development" else "regression"
        result = validate_items([self.questions[1], leaked], BENCHMARK, self.manifest)
        self.assertIn("split_leakage", {i["code"] for i in result["issues"]})


if __name__ == "__main__":
    unittest.main()
