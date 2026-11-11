"""Bounded unit checks for durable pause/cancel transitions."""

import json
import sqlite3
import tempfile
import threading
import time
import unittest

from app.indexing.repository import JobCancelled, JobRepository
from app.storage.database import Database
from app.api import create_app
from app.bootstrap import create_services
from fastapi.testclient import TestClient


class JobControlTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="rag-job-control-")
        self.addCleanup(self.temporary.cleanup)
        self.database = Database(self.temporary.name)
        self.jobs = JobRepository(self.database.connect, lambda _kb_id: None)
        self.kb_id = "a" * 32
        self.expected_build = {"schema_version": 1}
        with self.database.connect() as connection:
            connection.execute(
                "INSERT INTO knowledge_bases(id,data,revision) VALUES(?,?,1)",
                (self.kb_id, json.dumps({"build": self.expected_build})),
            )

    def enqueue_and_claim(self):
        job = self.jobs.enqueue(self.kb_id, "build", {"full": False})
        self.assertEqual(self.jobs.claim()["id"], job["id"])
        return job

    def wait_for_status(self, job_id, status):
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            if self.jobs.job(job_id)["status"] == status:
                return
            time.sleep(0.01)
        self.fail(f"job did not reach {status}")

    def test_schema_v1_migrates_in_place(self):
        legacy_root = tempfile.TemporaryDirectory(prefix="rag-job-migration-")
        self.addCleanup(legacy_root.cleanup)
        path = f"{legacy_root.name}/catalog.sqlite3"
        connection = sqlite3.connect(path)
        connection.execute(
            "CREATE TABLE jobs(id TEXT PRIMARY KEY,kb_id TEXT NOT NULL,operation TEXT NOT NULL,payload TEXT NOT NULL,status TEXT NOT NULL,stage TEXT NOT NULL,created REAL NOT NULL,updated REAL NOT NULL,error TEXT,result TEXT,idempotency TEXT UNIQUE)"
        )
        connection.execute("PRAGMA user_version=1")
        connection.commit()
        connection.close()
        migrated = Database(legacy_root.name)
        with migrated.connect() as connection:
            columns = {row["name"] for row in connection.execute("PRAGMA table_info(jobs)")}
            version = connection.execute("PRAGMA user_version").fetchone()[0]
        self.assertIn("control_request", columns)
        self.assertEqual(version, 2)

    def test_queued_job_can_pause_resume_and_cancel(self):
        job = self.jobs.enqueue(self.kb_id, "build", {"full": False})
        self.assertEqual(self.jobs.control(job["id"], "pause")["stage"], "paused_queued")
        self.assertEqual(self.jobs.control(job["id"], "resume")["status"], "queued")
        self.assertEqual(self.jobs.control(job["id"], "cancel")["status"], "cancelled")
        self.assertIsNone(self.jobs.job(job["id"])["control_request"])

    def test_running_job_pauses_at_checkpoint_and_resumes(self):
        job = self.enqueue_and_claim()
        self.jobs.control(job["id"], "pause")
        errors = []

        def checkpoint():
            try:
                self.jobs.checkpoint(job["id"], poll_seconds=0.01)
            except Exception as error:  # surfaced to the test thread below
                errors.append(error)

        thread = threading.Thread(target=checkpoint)
        thread.start()
        self.wait_for_status(job["id"], "paused")
        self.jobs.control(job["id"], "resume")
        thread.join(timeout=3)
        self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(self.jobs.job(job["id"])["status"], "running")

    def test_cancel_at_checkpoint_never_enters_publish(self):
        job = self.enqueue_and_claim()
        self.jobs.control(job["id"], "cancel")
        with self.assertRaises(JobCancelled):
            with self.jobs.publish_guard(job["id"], self.kb_id, self.expected_build):
                self.fail("cancelled task entered publication")
        self.jobs.finish(job["id"], cancelled=True)
        saved = self.jobs.job(job["id"])
        self.assertEqual(saved["status"], "cancelled")
        self.assertEqual(saved["stage"], "cancelled")

    def test_publish_transition_rejects_late_cancel(self):
        job = self.enqueue_and_claim()
        with self.jobs.publish_guard(job["id"], self.kb_id, self.expected_build):
            pass
        self.assertEqual(self.jobs.job(job["id"])["stage"], "publishing")
        with self.assertRaisesRegex(ValueError, "最后发布步骤"):
            self.jobs.control(job["id"], "cancel")

    def test_pause_waits_before_publish_until_resumed(self):
        job = self.enqueue_and_claim()
        self.jobs.control(job["id"], "pause")
        entered = threading.Event()
        errors = []

        def publish():
            try:
                with self.jobs.publish_guard(job["id"], self.kb_id, self.expected_build):
                    entered.set()
            except Exception as error:
                errors.append(error)

        thread = threading.Thread(target=publish)
        thread.start()
        time.sleep(0.05)
        self.assertFalse(entered.is_set())
        self.jobs.control(job["id"], "resume")
        thread.join(timeout=3)
        self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])
        self.assertTrue(entered.is_set())


class JobControlAPITests(unittest.TestCase):
    def test_queue_controls_are_exposed_to_admin(self):
        temporary = tempfile.TemporaryDirectory(prefix="rag-job-control-api-")
        self.addCleanup(temporary.cleanup)
        token = "job-control-api-test-administrator-token"
        service = create_services(temporary.name, admin_token=token)
        client = TestClient(create_app(service, with_mcp=False), base_url="http://127.0.0.1")
        with client:
            headers = {"Authorization": "Bearer " + token}
            base = client.post(
                "/api/v1/knowledge-bases", headers=headers, json={"name": "controls"}
            )
            self.assertEqual(base.status_code, 201, base.text)
            kb_id = base.json()["id"]
            task = client.post(
                f"/api/v1/knowledge-bases/{kb_id}/jobs", headers=headers, json={}
            )
            self.assertEqual(task.status_code, 202, task.text)
            job_id = task.json()["id"]
            paused = client.post(
                f"/api/v1/jobs/{job_id}/control",
                headers=headers,
                json={"action": "pause"},
            )
            self.assertEqual(paused.status_code, 200, paused.text)
            self.assertEqual(paused.json()["stage"], "paused_queued")
            cancelled = client.post(
                f"/api/v1/jobs/{job_id}/control",
                headers=headers,
                json={"action": "cancel"},
            )
            self.assertEqual(cancelled.status_code, 200, cancelled.text)
            self.assertEqual(cancelled.json()["status"], "cancelled")



if __name__ == "__main__":
    unittest.main()
