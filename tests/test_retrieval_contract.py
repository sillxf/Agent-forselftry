"""Bounded offline checks for query-time contracts; no real models or paid calls."""

import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from app.api import create_app
from app.bootstrap import create_services
from app.core.contracts import ModelConfig
from app.core.exceptions import BusyError
from app.indexing.worker import Worker
from app.models.embedding.provider import EmbeddingProvider
from app.models.pool import ModelPool, usage_context
from app.models.reranking.remote import RemoteRerankerProvider
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
        with closing(
            sqlite3.connect(self.service.root / "catalog.sqlite3")
        ) as connection, connection:
            data = json.loads(
                connection.execute(
                    "SELECT data FROM knowledge_bases WHERE id=?", (kb,)
                ).fetchone()[0]
            )
            data["profile"].pop("max_context_tokens")
            data["profile"]["max_context_chars"] = 24000
            connection.execute(
                "UPDATE knowledge_bases SET data=? WHERE id=?",
                (json.dumps(data), kb),
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
        with self.assertRaises(BusyError), pool.use("model", object):
            pass
        self.assertFalse(issubclass(BusyError, OSError))

    def test_a_busy_model_does_not_block_other_models(self):
        import os
        import threading

        pool = ModelPool(2)
        held, release = threading.Event(), threading.Event()

        def rerank():
            with pool.use("reranker", object):
                held.set()
                release.wait(5)

        owner = threading.Thread(target=rerank)
        owner.start()
        self.addCleanup(owner.join)
        self.addCleanup(release.set)
        held.wait(5)
        os.environ["RAG_MODEL_ACQUIRE_TIMEOUT_SECONDS"] = "0.05"
        self.addCleanup(os.environ.pop, "RAG_MODEL_ACQUIRE_TIMEOUT_SECONDS")
        with pool.use("embedding", object), pool.use("embedding", object):
            pass
        with self.assertRaises(BusyError), pool.use("reranker", object):
            pass
        # The pool is full and the reranker is in use: evict the idle model only.
        with pool.use("third", object):
            pass
        self.assertEqual(set(pool.models), {"reranker", "third"})
        release.set()
        owner.join()
        self.assertEqual(pool.models["reranker"].users, 0)

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


    def test_error_codes_separate_input_state_and_damage(self):
        from app import __version__

        kb = self.base("Codes", {"a.md": "evidence"})
        unbuilt = self.request("POST", "/knowledge-bases", json={"name": "Empty"})["id"]

        def post(body):
            return self.client.post(
                "/api/v1/search",
                headers={"Authorization": "Bearer " + TOKEN},
                json={"query": "evidence", "knowledge_base_ids": [kb], **body},
            )

        bad_filter = post({"filters": {"nope": "x"}})
        self.assertEqual(bad_filter.status_code, 422)
        self.assertEqual(bad_filter.json()["code"], "invalid_request")
        self.assertEqual(post({"as_of": "yesterday"}).status_code, 422)
        self.assertEqual(post({"as_of": "2000-01-01T00:00:00"}).status_code, 422)
        only_unbuilt = post({"knowledge_base_ids": [unbuilt]})
        self.assertEqual(only_unbuilt.status_code, 409)
        self.assertEqual(only_unbuilt.json()["code"], "not_published")
        # An unbuilt base in a multi-base search is skipped with a warning.
        mixed = post({"knowledge_base_ids": [kb, unbuilt]})
        self.assertEqual(mixed.status_code, 200, mixed.text)
        self.assertTrue(mixed.json()["results"])
        self.assertIn(f"not_published:{unbuilt}", mixed.json()["metadata"]["warnings"])

        manifest = next(
            (self.service.workspaces.get(kb).repository.root).glob("*/faiss.index")
        )
        manifest.write_bytes(manifest.read_bytes() + b"x")
        self.service.retrieval.sessions.discard(kb)
        damaged = post({})
        self.assertEqual(damaged.status_code, 503, damaged.text)
        self.assertEqual(damaged.json()["code"], "index_integrity")
        live = self.client.get("/health/live").json()
        self.assertEqual(live["version"], __version__)

    def test_file_permission_error_is_not_reported_as_rate_limit(self):
        from unittest.mock import patch

        kb = self.base("Locked", {"a.md": "evidence"})
        document = self.request("GET", f"/knowledge-bases/{kb}/documents")[0]
        with patch(
            "app.knowledge.purge.remove_managed",
            side_effect=PermissionError(13, "file is in use"),
        ):
            response = self.client.delete(
                f"/api/v1/knowledge-bases/{kb}/documents/"
                f"{document['document_id']}?confirm=true",
                headers={"Authorization": "Bearer " + TOKEN},
            )
        self.assertEqual(response.status_code, 503, response.text)
        self.assertNotIn("Rate limit", response.text)
        key = self.request(
            "POST",
            "/keys",
            json={"name": "one", "knowledge_base_ids": [kb], "requests_per_minute": 1},
        )
        reader = {"Authorization": "Bearer " + key["token"]}
        body = {"query": "evidence", "knowledge_base_ids": [kb]}
        self.assertEqual(self.client.post("/api/v1/search", json=body, headers=reader).status_code, 200)
        limited = self.client.post("/api/v1/search", json=body, headers=reader)
        self.assertEqual(limited.status_code, 429)
        self.assertEqual(limited.headers["Retry-After"], "60")


    def test_inspection_reuses_verified_snapshot_until_files_change(self):
        from unittest.mock import patch

        kb = self.base("Reads", {"a.md": "evidence one", "b.md": "evidence two"})
        hit = self.search([kb], "evidence")["results"][0]
        repository = self.service.workspaces.get(kb).repository
        path = f"/knowledge-bases/{kb}/chunks/{hit['chunk_id']}"
        loads, hashes = [], []
        original_load, original_hash = repository._load_generation, None
        import app.storage.snapshot_repository as module

        original_hash = module.file_checksum

        def counted_load(*args, **kwargs):
            loads.append(args)
            return original_load(*args, **kwargs)

        def counted_hash(path):
            hashes.append(path)
            return original_hash(path)

        with patch.object(repository, "_load_generation", side_effect=counted_load), \
                patch.object(module, "file_checksum", side_effect=counted_hash):
            for _ in range(3):
                self.request("GET", path)
                self.request("GET", f"/knowledge-bases/{kb}/documents/{hit['document_id']}")
                self.request("GET", f"/knowledge-bases/{kb}/documents")
        self.assertEqual(loads, [])  # The search already loaded the generation.
        self.assertEqual(hashes, [])  # Verified once, not on every read.
        # A private load (builds, deletion) does not evict the shared copy.
        generation = repository.current_pointer()["generation"]
        shared = repository.load_generation(generation, cached=True)
        self.assertIsNot(repository.load_generation(generation), shared)
        self.assertIs(repository.load_generation(generation, cached=True), shared)

        generation = repository.current_pointer()["generation"]
        chunks = repository.root / generation / "chunks.jsonl"
        chunks.write_bytes(chunks.read_bytes() + b"\n")
        damaged = self.client.get(
            "/api/v1" + path, headers={"Authorization": "Bearer " + TOKEN}
        )
        self.assertEqual(damaged.status_code, 503, damaged.text)


    def test_remote_reranker_and_pooled_embedding_client(self):
        seen = []

        def handler(request):
            seen.append(request)
            body = json.loads(request.content)
            if request.url.path.endswith("/rerank"):
                scores = [0.1, 0.9, 0.5][: len(body["documents"])]
                return httpx.Response(200, json={"results": [
                    {"index": i, "relevance_score": s} for i, s in enumerate(scores)]})
            return httpx.Response(200, json={"data": [
                {"index": i, "embedding": [1.0, 0.0]} for i in range(len(body["input"]))]})

        transport = httpx.MockTransport(handler)
        config = ModelConfig(kind="reranker", provider="cohere_compatible",
                             model="rerank-x", base_url="https://rerank.example/v1")
        reranker = RemoteRerankerProvider(config, transport=transport)
        usage = []
        token = usage_context.set(usage)
        self.addCleanup(usage_context.reset, token)
        ranked = reranker.rerank("q", [{"content": "a"}, {"content": "b"}, {"content": "c"}])
        self.assertEqual([x["content"] for x in ranked], ["b", "c", "a"])
        self.assertEqual(seen[0].url, "https://rerank.example/v1/rerank")
        self.assertEqual(usage[0]["provider"], "cohere_compatible")
        with self.assertRaises(ValueError):  # Embedding role cannot use it.
            ModelConfig(kind="embedding", provider="cohere_compatible",
                        model="x", base_url="https://e.example")

        embedding = EmbeddingProvider(
            {
                "kind": "embedding",
                "provider": "openai_compatible",
                "model": "e",
                "base_url": "https://e.example/v1",
                "dimension": 2,
                "tokenizer": "t",
            },
            None, transport=transport)
        embedding.embed_query(["one"])
        first = embedding._client
        embedding.embed_query(["two"])
        self.assertIs(embedding._client, first)


    def test_auto_gc_is_opt_in_and_status_reports_disk_use(self):
        import os

        kb = self.base("Retention", {"a.md": "evidence"})
        repository = self.service.workspaces.get(kb).repository

        def rebuild():
            job = self.request("POST", f"/knowledge-bases/{kb}/jobs", json={"full": True})
            self.assertTrue(Worker(self.service.indexing).run_once())
            return json.loads(self.service.indexing.jobs.job(job["id"])["result"])["output"]

        for _ in range(3):
            self.assertNotIn("gc", rebuild())
        self.assertEqual(repository.usage()["generations"], 4)
        status = self.request("GET", f"/knowledge-bases/{kb}/status")
        self.assertEqual(status["storage"]["generations"], 4)
        self.assertGreater(status["storage"]["index_bytes"], 0)

        os.environ.update(RAG_AUTO_GC="true", RAG_GC_KEEP="2", RAG_GC_MIN_AGE_SECONDS="0")
        for name in ("RAG_AUTO_GC", "RAG_GC_KEEP", "RAG_GC_MIN_AGE_SECONDS"):
            self.addCleanup(os.environ.pop, name)
        output = rebuild()
        self.assertEqual(len(output["gc"]["generations"]), 3)
        self.assertEqual(repository.usage()["generations"], 2)
        self.assertTrue(self.search([kb], "evidence")["results"])


if __name__ == "__main__":
    unittest.main()
