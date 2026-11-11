"""Caller-facing retrieval features: relevance, filters, neighbours, Dify adapter."""

from pathlib import Path
import tempfile
import unittest

from fastapi.testclient import TestClient

from app.api import create_app
from app.bootstrap import create_services
from app.indexing.worker import Worker
from app.retrieval.filters import compile_filters
from app.core.exceptions import InvalidRequest
from tests.support import FakeEmbedding, Parser

TOKEN = "retrieval-features-test-token-0123"


class FilterTests(unittest.TestCase):
    def test_operators(self):
        doc = {"metadata.year": "2024", "metadata.team": "Red", "file_type": "pdf"}
        get = doc.get

        def ok(f):
            return compile_filters(f)(get)

        self.assertTrue(ok({"file_type": "pdf"}))
        self.assertTrue(ok({"metadata.year": {"$gte": "2023", "$lt": "2025"}}))
        self.assertFalse(ok({"metadata.year": {"$gt": "2024"}}))
        self.assertTrue(ok({"metadata.year": {"$gt": "999"}}))  # Numeric, not text.
        self.assertTrue(ok({"metadata.team": {"$contains": "re"}}))
        self.assertTrue(ok({"metadata.team": {"$nin": ["Blue"]}}))
        self.assertTrue(ok({"metadata.owner": {"$exists": False}}))
        self.assertFalse(ok({"metadata.owner": "x"}))  # Missing never equals.
        self.assertTrue(ok({"metadata.owner": {"$ne": "x"}}))
        self.assertTrue(ok({"$or": [{"file_type": "md"}, {"metadata.team": ["Red"]}]}))
        self.assertFalse(ok({"$and": [{"file_type": "pdf"}, {"metadata.team": "Blue"}]}))
        for bad in (
            {"nope": "x"},
            {"metadata.a": {"$regex": "x"}},
            {"metadata.a": {"$in": "x"}},
            {"$or": []},
            {"metadata.a": {"$exists": "yes"}},
            {"metadata.a": True},
        ):
            with self.assertRaises(InvalidRequest, msg=bad):
                compile_filters(bad)


class FeatureTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="rag-features-")
        self.addCleanup(temporary.cleanup)
        self.service = create_services(
            Path(temporary.name) / "data",
            admin_token=TOKEN,
            embedding_factory=FakeEmbedding,
            parser_factory=lambda workspace, configuration: Parser(),
        )
        self.client = TestClient(create_app(self.service, with_mcp=False), base_url="http://127.0.0.1")
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)
        self.admin = {"Authorization": "Bearer " + TOKEN}
        self.kb = self.post("/knowledge-bases", {"name": "F", "build": {
            "ocr_enabled": False, "parent_tokens": 120, "child_tokens": 40, "overlap_tokens": 0}})["id"]
        long_text = " ".join(f"step{i} alpha" for i in range(60))
        for name, text in {"long.md": long_text, "red.md": "alpha red team note",
                           "blue.md": "unrelated beta words"}.items():
            self.client.post(f"/api/v1/knowledge-bases/{self.kb}/documents?filename={name}",
                             content=text.encode(), headers=self.admin)
        docs = {d["name"]: d["document_id"] for d in self.get(f"/knowledge-bases/{self.kb}/documents")}
        self.client.patch(f"/api/v1/knowledge-bases/{self.kb}/documents/{docs['red.md']}",
                          json={"metadata": {"team": "red", "year": "2025"}}, headers=self.admin)
        self.post(f"/knowledge-bases/{self.kb}/jobs", {})
        self.assertTrue(Worker(self.service.indexing).run_once())

    def get(self, path, **kw):
        r = self.client.get("/api/v1" + path, headers=kw.pop("headers", self.admin), **kw)
        self.assertTrue(r.is_success, r.text)
        return r.json()

    def post(self, path, body, headers=None):
        r = self.client.post("/api/v1" + path, json=body, headers=headers or self.admin)
        self.assertTrue(r.is_success, r.text)
        return r.json()

    def search(self, **body):
        return self.post("/search", {"query": "alpha", "knowledge_base_ids": [self.kb], **body})

    def test_relevance_min_score_and_filters(self):
        results = self.search(top_k=5)["results"]
        self.assertTrue(results)
        for r in results:
            self.assertEqual(r["relevance_source"], "similarity")
            self.assertTrue(0 <= r["relevance"] <= 1.0001)
        top = max(r["relevance"] for r in results)
        kept = self.search(top_k=5, min_score=top)["results"]
        self.assertTrue(kept and all(r["relevance"] >= top for r in kept))
        only = self.search(filters={"metadata.year": {"$gte": "2024"}})["results"]
        self.assertEqual({r["source"] for r in only}, {"red.md"})
        either = self.search(top_k=20, filters={"$or": [{"source": "long.md"}, {"metadata.team": "red"}]})
        self.assertEqual({r["source"] for r in either["results"]}, {"long.md", "red.md"})
        bad = self.client.post("/api/v1/search", headers=self.admin, json={
            "query": "alpha", "knowledge_base_ids": [self.kb], "filters": {"metadata.x": {"$regex": "a"}}})
        self.assertEqual(bad.status_code, 422)

    def test_neighbouring_chunks_and_sections(self):
        hits = self.search(top_k=5, filters={"source": "long.md"})["results"]
        children = [c for c in self.service.workspaces.get(self.kb).repository.load_generation(
            self.service.workspaces.get(self.kb).repository.current_pointer()["generation"],
            cached=True).store.records if c["source_name"] == "long.md"]
        self.assertGreater(len(children), 3)
        middle = children[2]["chunk_id"]
        context = self.get(f"/knowledge-bases/{self.kb}/chunks/{middle}/context?before=2&after=1")
        self.assertEqual([i["offset"] for i in context["items"]], [-2, -1, 0, 1])
        self.assertEqual([i["chunk_id"] for i in context["items"]],
                         [c["chunk_id"] for c in children[0:4]])
        self.assertEqual(context["total"], len(children))
        sections = self.get(f"/knowledge-bases/{self.kb}/chunks/{middle}/context?unit=parent&after=5")
        self.assertIn(0, [i["offset"] for i in sections["items"]])
        self.assertNotIn("blocks", sections["items"][0])
        self.assertTrue(hits)
        too_many = self.client.get(f"/api/v1/knowledge-bases/{self.kb}/chunks/{middle}/context?before=9",
                                   headers=self.admin)
        self.assertEqual(too_many.status_code, 422)
        docs = {d["name"]: d["document_id"] for d in self.get(f"/knowledge-bases/{self.kb}/documents")}
        self.client.post(f"/api/v1/knowledge-bases/{self.kb}/documents/{docs['long.md']}/trash",
                         headers=self.admin)
        gone = self.client.get(f"/api/v1/knowledge-bases/{self.kb}/chunks/{middle}/context",
                               headers=self.admin)
        self.assertEqual(gone.status_code, 404)

    def test_dify_external_knowledge_contract(self):
        key = self.post("/keys", {"name": "dify", "knowledge_base_ids": [self.kb]})
        reader = {"Authorization": "Bearer " + key["token"]}
        body = {"knowledge_id": self.kb, "query": "alpha",
                "retrieval_setting": {"top_k": 2, "score_threshold": 0.0}}
        response = self.client.post("/api/v1/dify/retrieval", json=body, headers=reader)
        self.assertEqual(response.status_code, 200, response.text)
        records = response.json()["records"]
        self.assertEqual(len(records), 2)
        self.assertEqual(set(records[0]), {"content", "score", "title", "metadata"})
        self.assertIsInstance(records[0]["metadata"], dict)
        # Order is the service's hybrid ranking; score is similarity and may differ.
        self.assertTrue(all(0 <= r["score"] <= 1.0001 for r in records))
        filtered = self.client.post("/api/v1/dify/retrieval", headers=reader, json=dict(
            body, metadata_condition={"logical_operator": "and", "conditions": [
                {"name": "team", "comparison_operator": "is", "value": "red"}]})).json()
        self.assertEqual({r["title"] for r in filtered["records"]}, {"red.md"})
        empty = self.client.post("/api/v1/dify/retrieval", headers=reader,
                                 json=dict(body, retrieval_setting={"top_k": 2, "score_threshold": 1.0}))
        self.assertEqual(empty.json(), {"records": []})
        other = self.post("/knowledge-bases", {"name": "other"})["id"]
        denied = self.client.post("/api/v1/dify/retrieval", headers=reader,
                                  json=dict(body, knowledge_id=other))
        self.assertEqual(denied.json()["error_code"], 1002)
        missing = self.client.post("/api/v1/dify/retrieval", headers=self.admin,
                                   json=dict(body, knowledge_id="f" * 32))
        self.assertEqual(missing.json()["error_code"], 2001)
        bad_key = self.client.post("/api/v1/dify/retrieval", json=body,
                                   headers={"Authorization": "Bearer wrong"})
        self.assertEqual((bad_key.status_code, bad_key.json()["error_code"]), (401, 1002))


if __name__ == "__main__":
    unittest.main()
