"""Bounded offline checks for query-time contracts; no real models or paid calls."""

from pathlib import Path
import sqlite3
import json
import tempfile
import unittest

from fastapi.testclient import TestClient

from app.api import create_app
from app.bootstrap import create_services
from app.core.exceptions import BusyError
from app.indexing.worker import Worker
from app.models.pool import ModelPool
from app.retrieval.policy import RetrievalPolicy
from tests.support import FakeEmbedding, Parser

TOKEN = "local-retrieval-contract-test-token"


class RetrievalContractTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="rag-contract-test-")
        self.addCleanup(temporary.cleanup)
        self.service = create_services(
            Path(temporary.name) / "data",
            admin_token=TOKEN,
            embedding_factory=FakeEmbedding,
            parser_factory=lambda workspace, configuration: Parser(),
        )
        self.client = TestClient(
            create_app(self.service, with_mcp=False), base_url="http://127.0.0.1"
        )
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

    def request(self, method, path, **kwargs):
        response = self.client.request(
            method,
            "/api/v1" + path,
            headers={"Authorization": "Bearer " + TOKEN},
            **kwargs,
        )
        self.assertTrue(response.is_success, (response.status_code, response.text))
        return response.json()

    def base(self, name, documents, **profile):
        kb = self.request(
            "POST",
            "/knowledge-bases",
            json={"name": name, "build": {"ocr_enabled": False}, "profile": profile},
        )["id"]
        for filename, text in documents.items():
            self.request(
                "POST",
                f"/knowledge-bases/{kb}/documents?filename={filename}",
                content=text.encode(),
            )
        job = self.request("POST", f"/knowledge-bases/{kb}/jobs", json={})
        self.assertTrue(Worker(self.service.indexing).run_once())
        self.assertEqual(
            self.service.indexing.jobs.job(job["id"])["status"], "succeeded"
        )
        return kb

    def search(self, kb_ids, query, **extra):
        return self.request(
            "POST",
            "/search",
            json={
                "query": query,
                "knowledge_base_ids": kb_ids,
                "include_trace": True,
                **extra,
            },
        )

    def test_additional_queries_are_fused_without_model_generation(self):
        kb = self.base(
            "Fusion",
            {
                "english.md": "Credential dumping from LSASS memory.",
                "other.md": "Unrelated firewall maintenance notes.",
            },
        )
        # The original wording matches the wrong document; the caller's rewrites
        # (as a translation would) match the right one and must win after fusion.
        question = "firewall maintenance 凭据转储"
        alone = self.search([kb], question, top_k=1)
        self.assertEqual(alone["results"][0]["source"], "other.md")
        fused = self.search(
            [kb],
            question,
            top_k=1,
            queries=["credential dumping LSASS", "LSASS memory credential"],
        )
        self.assertEqual(fused["results"][0]["source"], "english.md")
        self.assertEqual(fused["trace"][0]["query_count"], 3)
        self.assertEqual(
            {r["query_index"] for r in fused["trace"][0]["routes"]}, {0, 1, 2}
        )
        self.assertEqual(fused["metadata"]["model_usage"], [])
        blank = self.client.post(
            "/api/v1/search",
            headers={"Authorization": "Bearer " + TOKEN},
            json={"query": "x", "knowledge_base_ids": [kb], "queries": [" "]},
        )
        self.assertEqual(blank.status_code, 422)

    def test_context_budget_is_counted_in_tokens(self):
        # Fake tokenizer: one token per character. Two 100-token parents.
        kb = self.base(
            "Budget",
            {"a.md": "alpha " + "a" * 94, "b.md": "alpha " + "b" * 94},
            max_context_tokens=150,
        )
        results = self.search([kb], "alpha", top_k=2)["results"]
        self.assertEqual(results[0]["context_tokens"], 100)
        self.assertLessEqual(sum(r["context_tokens"] for r in results), 150)
        self.assertEqual(len(results), 1)

    def test_profile_saved_with_character_budget_still_loads(self):
        legacy = RetrievalPolicy.model_validate({"max_context_chars": 24000})
        self.assertEqual(legacy.max_context_tokens, 8000)
        kb = self.base("Legacy", {"a.md": "legacy evidence"})
        with sqlite3.connect(self.service.root / "catalog.sqlite3") as connection:
            data = json.loads(
                connection.execute(
                    "SELECT data FROM knowledge_bases WHERE id=?", (kb,)
                ).fetchone()[0]
            )
            data["profile"].pop("max_context_tokens")
            data["profile"]["max_context_chars"] = 24000
            connection.execute(
                "UPDATE knowledge_bases SET data=? WHERE id=?", (json.dumps(data), kb)
            )
        self.assertTrue(self.search([kb], "legacy")["results"])

    def test_busy_model_pool_reports_busy_not_storage_failure(self):
        import os
        import threading

        pool = ModelPool(1)
        held, release = threading.Event(), threading.Event()

        def hold():  # The pool lock is reentrant, so another thread must own it.
            with pool.use("model", object):
                held.set()
                release.wait(5)

        owner = threading.Thread(target=hold)
        owner.start()
        self.addCleanup(owner.join)
        self.addCleanup(release.set)
        held.wait(5)
        os.environ["RAG_MODEL_ACQUIRE_TIMEOUT_SECONDS"] = "0.01"
        self.addCleanup(os.environ.pop, "RAG_MODEL_ACQUIRE_TIMEOUT_SECONDS")
        with self.assertRaises(BusyError):
            with pool.use("model", object):
                pass
        self.assertFalse(issubclass(BusyError, OSError))

    def test_supersede_hides_old_document_and_review_date_is_informational(self):
        kb = self.base("Lifecycle", {"old.md": "policy v1", "new.md": "policy v2"})
        documents = {
            d["name"]: d
            for d in self.request("GET", f"/knowledge-bases/{kb}/documents")
        }
        old, new = documents["old.md"]["document_id"], documents["new.md"]["document_id"]
        path = f"/knowledge-bases/{kb}/documents/"

        def sources():
            return {r["source"] for r in self.search([kb], "policy", top_k=5)["results"]}

        self.assertEqual(sources(), {"old.md", "new.md"})
        registry = self.service.workspaces.get(kb).registry
        revision = registry.revision
        self.request(
            "PUT", path + old + "/review", json={"review_after": "2000-01-01T00:00:00Z"}
        )
        self.assertEqual(registry.revision, revision)  # Does not stale a build.
        self.assertEqual(sources(), {"old.md", "new.md"})

        self.request("PUT", path + old + "/superseded-by", json={"superseded_by": new})
        self.assertEqual(sources(), {"new.md"})
        listed = {
            d["name"]: d
            for d in self.request("GET", f"/knowledge-bases/{kb}/documents")
        }
        self.assertEqual(listed["old.md"]["hidden_reason"], "superseded")
        self.assertTrue(listed["old.md"]["review_due"])
        self.assertIsNone(listed["new.md"]["hidden_reason"])

        cycle = self.client.put(
            "/api/v1" + path + new + "/superseded-by",
            headers={"Authorization": "Bearer " + TOKEN},
            json={"superseded_by": old},
        )
        self.assertEqual(cycle.status_code, 409)
        unbuilt = self.request(
            "POST",
            f"/knowledge-bases/{kb}/documents?filename=draft.md",
            content=b"policy v3 draft",
        )["document"]["document_id"]
        early = self.client.put(
            "/api/v1" + path + new + "/superseded-by",
            headers={"Authorization": "Bearer " + TOKEN},
            json={"superseded_by": unbuilt},
        )
        self.assertEqual(early.status_code, 409)
        self.assertIn("publish", early.json()["detail"])
        self.assertIn("new.md", sources())

        # The old document comes back once its replacement leaves live search.
        self.request("POST", path + new + "/trash")
        self.assertEqual(sources(), {"old.md"})
        self.request("POST", path + new + "/undelete")
        self.request("PUT", path + old + "/superseded-by", json={"superseded_by": None})
        self.assertEqual(sources(), {"old.md", "new.md"})

    def test_cross_base_order_uses_comparable_reranker_scores(self):
        scores = {"strong.md": 9.0, "weak.md": 0.1}

        class Reranker:
            def rerank(self, query, candidates):
                return sorted(
                    [
                        dict(c, reranker_score=scores.get(c["source_name"], 5.0))
                        for c in candidates
                    ],
                    key=lambda c: -c["reranker_score"],
                )

        self.service.retrieval.sessions.providers.reranker_factory = (
            lambda config: Reranker()
        )
        profile = {"default_strategy": "hybrid_rerank", "reranker_timeout_seconds": 30}
        weak = self.base("Weak", {"weak.md": "token weak"}, **profile)
        strong = self.base(
            "Strong",
            {"strong.md": "token strong", "strong2.md": "token strong again"},
            **profile,
        )
        results = self.search([weak, strong], "token", top_k=3)["results"]
        # Rank fusion alone would place weak.md second (rank 1 in its own base).
        self.assertEqual(
            [r["source"] for r in results], ["strong.md", "strong2.md", "weak.md"]
        )


if __name__ == "__main__":
    unittest.main()
