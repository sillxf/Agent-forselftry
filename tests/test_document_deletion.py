"""Bounded offline deletion checks; temporary data, no real models or paid calls."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from filelock import FileLock

from app.api import create_app
from app.bootstrap import create_services
from app.indexing.worker import Worker
from app.knowledge.purge import remove_managed
from tests.support import FakeEmbedding, Parser

TOKEN = "local-deletion-test-administrator-token"


class DocumentDeletionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="rag-delete-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.service = create_services(
            self.root / "data",
            admin_token=TOKEN,
            embedding_factory=FakeEmbedding,
            parser_factory=lambda workspace, configuration: Parser(),
        )
        self.client = TestClient(
            create_app(self.service, with_mcp=False), base_url="http://127.0.0.1"
        )
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)
        self.headers = {"Authorization": "Bearer " + TOKEN}
        self.kb = self.request(
            "POST",
            "/knowledge-bases",
            json={
                "name": "Deletion test",
                "build": {"ocr_enabled": False},
            },
        )["id"]
        self.workspace = self.service.workspaces.get(self.kb)

    def response(self, method, path, **kwargs):
        return self.client.request(
            method,
            "/api/v1" + path,
            headers=kwargs.pop("headers", self.headers),
            **kwargs,
        )

    def request(self, method, path, **kwargs):
        result = self.response(method, path, **kwargs)
        self.assertTrue(result.is_success, (result.status_code, result.text))
        return result.json()

    def upload(self, filename, content=b"target evidence"):
        return self.request(
            "POST",
            f"/knowledge-bases/{self.kb}/documents?filename={filename}",
            content=content,
        )["document"]["document_id"]

    def build(self):
        job = self.request("POST", f"/knowledge-bases/{self.kb}/jobs", json={})
        self.assertTrue(Worker(self.service.indexing).run_once())
        self.assertEqual(
            self.service.indexing.jobs.job(job["id"])["status"], "succeeded"
        )
        return self.workspace.repository.current_pointer()["generation"]

    def path(self, document):
        return f"/knowledge-bases/{self.kb}/documents/{document}"

    def delete(self, document):
        return self.request("DELETE", self.path(document) + "?confirm=true")

    def search_ids(self):
        result = self.request(
            "POST",
            "/search",
            json={
                "query": "evidence",
                "knowledge_base_ids": [self.kb],
                "top_k": 10,
            },
        )
        return {r["document_id"] for r in result["results"]}

    def test_published_delete_preserves_other_documents_and_retires_only_duplicates(
        self,
    ):
        target = self.upload("target.md")
        survivor = self.upload("survivor.md", b"survivor evidence")
        old = self.build()
        self.assertIn(target, self.search_ids())  # Warm an existing query runtime.
        original = Path(self.workspace.registry.get_document(target).source_path)
        blob = Path(self.workspace.registry.list_versions(target)[0].source_blob_path)
        sources = [original, blob]
        jobs = self.service.indexing.jobs
        duplicate = jobs.enqueue(self.kb, "purge", {"document_id": target})
        unrelated = jobs.enqueue(self.kb, "purge", {"document_id": survivor})
        build = jobs.enqueue(self.kb, "build", {})
        config = self.service.knowledge.repository.kb(self.kb)
        config["build"]["child_tokens"] = 250
        self.request(
            "PUT",
            f"/knowledge-bases/{self.kb}?revision={config['revision']}",
            json={k: config[k] for k in ("name", "description", "build", "profile")},
        )
        with (
            patch.object(
                self.service.indexing,
                "parser_factory",
                side_effect=AssertionError("parser loaded"),
            ),
            patch.object(
                self.service.indexing.providers,
                "embedding",
                side_effect=AssertionError("model loaded"),
            ),
            patch.object(
                self.service.indexing.factory,
                "create",
                side_effect=AssertionError("pipeline loaded"),
            ),
        ):
            result = self.delete(target)
        self.assertEqual(result["status"], "completed")
        self.assertFalse(any(p.exists() for p in sources))
        self.assertFalse((self.workspace.repository.root / old).exists())
        clean = self.workspace.repository.current_pointer()
        self.assertEqual(
            clean["signature"]["child_tokens"], 400
        )  # Not the pending config.
        self.assertEqual(self.search_ids(), {survivor})
        snapshot = self.workspace.repository.load_generation(clean["generation"])
        self.assertEqual({d.document_id for d in snapshot.documents}, {survivor})
        self.assertEqual(jobs.job(duplicate["id"])["status"], "succeeded")
        for pending in (unrelated, build):
            self.assertEqual(jobs.job(pending["id"])["status"], "queued")
        self.assertEqual(self.delete(target), result)  # Idempotent HTTP retry.
        self.assertEqual(
            self.response("POST", self.path(target) + "/undelete").status_code, 409
        )
        rows = self.request("GET", f"/knowledge-bases/{self.kb}/documents")
        self.assertEqual({d["document_id"] for d in rows}, {survivor})
        # Deleting the last published document leaves a valid, searchable empty index.
        self.assertEqual(self.delete(survivor)["status"], "completed")
        self.assertEqual(self.search_ids(), set())

    def test_unpublished_delete_retry_and_shared_blob(self):
        target = self.upload("target.md")
        survivor = self.upload("same-bytes.md")
        original = Path(self.workspace.registry.get_document(target).source_path)
        blob = Path(self.workspace.registry.list_versions(target)[0].source_blob_path)

        def fail_original(path, root):
            if Path(path) == original:
                raise OSError("simulated interruption")
            return remove_managed(path, root)

        with patch("app.knowledge.purge.remove_managed", side_effect=fail_original):
            response = self.response("DELETE", self.path(target) + "?confirm=true")
        self.assertEqual(response.status_code, 503)
        rows = self.request("GET", f"/knowledge-bases/{self.kb}/documents")
        self.assertEqual(
            next(d for d in rows if d["document_id"] == target)["status"],
            "purge_incomplete",
        )
        self.assertEqual(self.delete(target)["status"], "completed")
        self.assertFalse(original.exists())
        self.assertTrue(
            blob.exists()
        )  # Shared immutable bytes still belong to survivor.
        self.assertIsNone(self.workspace.repository.current_pointer())
        self.assertEqual(self.service.indexing.jobs.jobs(), [])
        self.assertEqual(self.delete(survivor)["status"], "completed")
        self.assertFalse(blob.exists())

    def test_confirmation_authorization_and_busy_do_not_delete_or_enqueue(self):
        target = self.upload("target.md")
        original = Path(self.workspace.registry.get_document(target).source_path)
        self.assertEqual(self.response("DELETE", self.path(target)).status_code, 409)
        reader = self.request(
            "POST",
            "/keys",
            json={
                "name": "read-only",
                "knowledge_base_ids": [self.kb],
            },
        )
        self.assertEqual(
            self.response(
                "DELETE",
                self.path(target) + "?confirm=true",
                headers={
                    "Authorization": "Bearer " + reader["token"],
                },
            ).status_code,
            403,
        )
        with FileLock(str(self.workspace.storage_dir / "build.lock"), timeout=0):
            self.assertEqual(
                self.response(
                    "DELETE", self.path(target) + "?confirm=true"
                ).status_code,
                409,
            )
        self.assertTrue(original.exists())
        self.assertIsNone(self.workspace.registry.get_document(target).purged_at)
        self.assertEqual(
            self.response(
                "POST",
                f"/knowledge-bases/{self.kb}/jobs",
                json={
                    "operation": "purge",
                    "document_id": target,
                    "confirm": True,
                },
            ).status_code,
            409,
        )
        self.assertEqual(self.service.indexing.jobs.jobs(), [])
        self.request("POST", self.path(target) + "/trash")
        self.assertTrue(original.exists())
        self.request("POST", self.path(target) + "/undelete")
        self.delete(target)

    def test_published_interruption_resumes_without_restoring_deleted_content(self):
        target = self.upload("target.md")
        old = self.build()
        generation = self.workspace.repository.root / old

        def fail_old_snapshot(path, root):
            if Path(path) == generation:
                raise OSError("simulated removal failure after clean publication")
            return remove_managed(path, root)

        with patch("app.knowledge.purge.remove_managed", side_effect=fail_old_snapshot):
            self.assertEqual(
                self.response(
                    "DELETE", self.path(target) + "?confirm=true"
                ).status_code,
                503,
            )
        self.assertEqual(self.search_ids(), set())
        self.assertTrue(generation.exists())
        self.assertEqual(self.delete(target)["status"], "completed")
        self.assertFalse(generation.exists())
        self.assertEqual(self.search_ids(), set())

    def test_removal_refuses_paths_outside_managed_root(self):
        outside = self.root / "outside.txt"
        outside.write_text("must survive", encoding="utf-8")
        with self.assertRaises(ValueError):
            remove_managed(outside, self.workspace.storage_dir)
        with self.assertRaises(ValueError):
            remove_managed(self.workspace.storage_dir, self.workspace.storage_dir)
        self.assertTrue(outside.exists())

    def test_knowledge_base_delete_cleans_data_jobs_scopes_and_cached_handles(self):
        document = self.upload("target.md")
        self.build()
        self.assertIn(document, self.search_ids())
        other = self.request(
            "POST", "/knowledge-bases", json={"name": "Keep this base"}
        )["id"]
        single = self.request(
            "POST", "/keys", json={"name": "single", "knowledge_base_ids": [self.kb]}
        )
        shared = self.request(
            "POST",
            "/keys",
            json={"name": "shared", "knowledge_base_ids": [self.kb, other]},
        )
        jobs = self.service.indexing.jobs
        jobs.enqueue(self.kb, "build", {})
        jobs.enqueue(self.kb, "purge", {"document_id": document})
        retained = jobs.enqueue(other, "build", {})
        external = self.root / "external-original.md"
        external.write_text("External original must survive", encoding="utf-8")
        self.workspace.lifecycle.import_document(external)
        other_upload = self.request(
            "POST",
            f"/knowledge-bases/{other}/documents?filename=keep.md",
            content=b"Preserve another base's original",
        )
        other_original = Path(
            self.service.workspaces.get(other)
            .registry.get_document(other_upload["document"]["document_id"])
            .source_path
        )
        models = self.request("GET", "/models")
        result = self.request("DELETE", f"/knowledge-bases/{self.kb}?confirm=true")
        self.assertTrue(external.exists())
        self.assertTrue(other_original.exists())
        self.assertEqual(result["status"], "completed")
        self.assertFalse((self.service.root / "bases" / self.kb).exists())
        self.assertTrue((self.service.root / "bases" / other).exists())
        self.assertEqual(jobs.jobs(self.kb), [])
        self.assertEqual(jobs.job(retained["id"])["status"], "queued")
        self.assertEqual(self.request("GET", "/models"), models)
        self.assertNotIn(self.kb, self.service.workspaces._items)
        self.assertFalse(
            any(key[0] == self.kb for key in self.service.retrieval.sessions._items)
        )
        self.assertEqual(self.response("GET", self.path(document)).status_code, 404)
        self.assertEqual(
            self.response(
                "GET",
                "/knowledge-bases",
                headers={"Authorization": "Bearer " + single["token"]},
            ).status_code,
            401,
        )
        bases = self.request(
            "GET",
            "/knowledge-bases",
            headers={"Authorization": "Bearer " + shared["token"]},
        )
        self.assertEqual([b["id"] for b in bases], [other])
        keys = {key["id"]: key for key in self.request("GET", "/keys")}
        self.assertEqual(keys[shared["id"]]["knowledge_base_ids"], [other])
        self.assertTrue(keys[single["id"]]["revoked"])
        self.assertEqual(
            self.request("DELETE", f"/knowledge-bases/{self.kb}?confirm=true"), result
        )
        # Last-base deletion is supported; it must not force a default base back into existence.
        self.request("DELETE", f"/knowledge-bases/{other}?confirm=true")
        self.assertEqual(self.request("GET", "/knowledge-bases"), [])
        self.assertTrue(
            self.request("POST", "/knowledge-bases", json={"name": "Start again"})["id"]
        )

    def test_knowledge_base_partial_failure_is_durable_and_retryable(self):
        document = self.upload("target.md")
        original = Path(self.workspace.registry.get_document(document).source_path)
        base = self.service.root / "bases" / self.kb

        def fail_after_partial_removal(path, root):
            self.assertEqual(Path(path), base)
            original.unlink()
            raise OSError("simulated partial directory deletion")

        with patch(
            "app.knowledge.purge.remove_managed", side_effect=fail_after_partial_removal
        ):
            self.assertEqual(
                self.response(
                    "DELETE", f"/knowledge-bases/{self.kb}?confirm=true"
                ).status_code,
                503,
            )
        rows = self.request("GET", "/knowledge-bases")
        self.assertTrue(rows[0]["deleting"])
        self.assertEqual(self.response("GET", self.path(document)).status_code, 409)
        self.assertEqual(
            self.response(
                "POST", f"/knowledge-bases/{self.kb}/jobs", json={}
            ).status_code,
            409,
        )
        self.assertEqual(
            self.response(
                "POST",
                f"/knowledge-bases/{self.kb}/documents?filename=new.md",
                content=b"must not recreate",
            ).status_code,
            409,
        )
        # A fresh service observes the marker even after a process restart.
        restarted = create_services(
            self.service.root, admin_token=TOKEN, embedding_factory=FakeEmbedding
        )
        admin = restarted.access.authenticate(TOKEN)
        self.assertTrue(restarted.knowledge.list(admin)[0]["deleting"])
        self.assertEqual(
            restarted.knowledge.delete(admin, self.kb)["status"], "completed"
        )
        self.assertFalse(base.exists())
        # A cached writer in the old service cannot recreate the deleted directory.
        with self.assertRaises(KeyError):
            self.service.documents.deleted(admin, self.kb, document)
        with self.assertRaises(KeyError):
            self.service.indexing.execute({"kb_id": self.kb, "operation": "build"}, {})
        self.assertFalse(base.exists())

    def test_knowledge_base_confirmation_authorization_and_busy_are_non_destructive(
        self,
    ):
        document = self.upload("target.md")
        self.build()
        self.assertIn(document, self.search_ids())
        path = f"/knowledge-bases/{self.kb}"
        self.assertEqual(self.response("DELETE", path).status_code, 409)
        key = self.request(
            "POST", "/keys", json={"name": "reader", "knowledge_base_ids": [self.kb]}
        )
        self.assertEqual(
            self.response(
                "DELETE",
                path + "?confirm=true",
                headers={"Authorization": "Bearer " + key["token"]},
            ).status_code,
            403,
        )
        gate = self.service.root / "locks" / (self.kb + ".lock")
        with FileLock(str(gate), timeout=0):
            self.assertEqual(
                self.response("DELETE", path + "?confirm=true").status_code, 409
            )
            self.assertIn(
                document, self.search_ids()
            )  # Maintenance does not block published reads.
        with FileLock(str(self.workspace.storage_dir / "build.lock"), timeout=0):
            self.assertEqual(
                self.response("DELETE", path + "?confirm=true").status_code, 409
            )
        self.assertFalse(
            self.service.knowledge.repository.kb(self.kb).get("deleting", False)
        )
        self.assertTrue(
            Path(self.workspace.registry.get_document(document).source_path).exists()
        )
        with self.assertRaises(ValueError):
            self.service.knowledge.delete(
                self.service.access.authenticate(TOKEN), "../outside"
            )

    def test_knowledge_base_retry_after_files_removed_but_metadata_cleanup_failed(self):
        self.upload("target.md")
        key = self.request(
            "POST", "/keys", json={"name": "reader", "knowledge_base_ids": [self.kb]}
        )
        with patch.object(
            self.service.access.keys,
            "remove_scope",
            side_effect=OSError("simulated catalog cleanup failure"),
        ):
            self.assertEqual(
                self.response(
                    "DELETE", f"/knowledge-bases/{self.kb}?confirm=true"
                ).status_code,
                503,
            )
        self.assertFalse((self.service.root / "bases" / self.kb).exists())
        self.assertTrue(self.request("GET", "/knowledge-bases")[0]["deleting"])
        self.assertEqual(
            self.request("DELETE", f"/knowledge-bases/{self.kb}?confirm=true")[
                "status"
            ],
            "completed",
        )
        self.assertEqual(self.request("GET", "/knowledge-bases"), [])
        keys = {item["id"]: item for item in self.request("GET", "/keys")}
        self.assertTrue(keys[key["id"]]["revoked"])


if __name__ == "__main__":
    unittest.main()
