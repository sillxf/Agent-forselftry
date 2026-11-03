"""Live lifecycle, nonblocking builds, cross-worker publication and crash recovery."""
import json
from datetime import datetime, timedelta, timezone
from threading import Event
from unittest.mock import Mock

from filelock import FileLock, Timeout
import pytest


def manual(factory):
    path = factory.knowledge / "manual.md"
    path.write_text("# Detection\n\nRepeated failed login attempts.", encoding="utf-8")
    return path


def generation(retriever):
    return retriever.repository.current_pointer()["generation"]


def test_delete_filters_dense_sparse_view_and_retained_pipelines_immediately(rag_factory):
    from app.rag.views import make_question_view
    manual(rag_factory)
    retriever = rag_factory()
    record = retriever.store.records[0]
    retriever.build_view_index([make_question_view(record, "How to detect failed logins?", "en", "test")])
    retained = retriever.pipeline
    document = retriever.documents[0]
    before = generation(retriever)
    retriever.lifecycle.delete(document.document_id)
    for strategy in ("dense", "bm25", "hybrid", "multi_view"):
        assert retained.search_rankings("failed login", 5, strategy)["parents"] == []
    assert retriever.search("failed login", 5) == []
    assert generation(retriever) == before
    revision = retriever.registry.revision
    retriever.lifecycle.delete(document.document_id)
    assert retriever.registry.revision == revision
    retriever.build_index()
    assert retriever.documents == []
    retriever.lifecycle.restore(document.document_id)
    retriever.build_index()
    assert retriever.documents[0].document_id == document.document_id
    assert retriever.search("failed login", 1)


def test_time_validity_is_checked_without_a_rebuild_or_scheduler(rag_factory):
    manual(rag_factory)
    retriever = rag_factory()
    document = retriever.documents[0]
    now = datetime.now(timezone.utc)
    before = generation(retriever)
    retriever.lifecycle.set_validity(document.document_id, effective_at=now + timedelta(days=1))
    assert retriever.search("login", 2) == []
    retriever.lifecycle.set_validity(document.document_id, expires_at=now - timedelta(seconds=1))
    assert retriever.search("login", 2) == []
    retriever.lifecycle.set_validity(document.document_id, effective_at=now - timedelta(days=1), expires_at=now + timedelta(days=1))
    assert retriever.search("login", 2)
    assert generation(retriever) == before
    revision = retriever.registry.revision
    with pytest.raises(ValueError, match="timezone"):
        retriever.lifecycle.set_validity(document.document_id, effective_at="2026-01-01T00:00:00")
    with pytest.raises(ValueError, match="later"):
        retriever.lifecycle.set_validity(document.document_id, effective_at=now, expires_at=now)
    assert retriever.registry.revision == revision


def test_background_build_does_not_hold_query_lock_and_rejects_concurrent_delete(rag_factory):
    source = manual(rag_factory)
    retriever = rag_factory()
    document = retriever.documents[0]
    before = generation(retriever)
    started, release = Event(), Event()
    parse = retriever.parser.parse
    def slow_parse(*args, **kwargs):
        started.set()
        assert release.wait(10)
        return parse(*args, **kwargs)
    retriever.parser.parse = slow_parse
    source.write_text("# Response\n\nIsolate compromised hosts.", encoding="utf-8")
    future = retriever.build_index_async()
    try:
        assert started.wait(10)
        assert retriever.build_index_async() is future
        assert "failed login" in retriever.search("failed login", 1)[0]["content"]
        retriever.lifecycle.delete(document.document_id)
        assert retriever.search("login", 1) == []
    finally:
        release.set()
    with pytest.raises(RuntimeError, match="Stale build"):
        future.result(timeout=10)
    assert generation(retriever) == before
    job = retriever.registry.list_jobs()[0]
    assert job["status"] == "failed" and "revision" in job["error_message"]


def test_cross_instance_file_lock_prevents_a_second_builder(rag_factory):
    manual(rag_factory)
    retriever = rag_factory()
    other = rag_factory(build=False)
    with FileLock(str(rag_factory.storage / "build.lock"), timeout=0):
        with pytest.raises(Timeout):
            other.build_index()
    assert retriever.search("login", 1)
    assert all(job["status"] == "succeeded" for job in retriever.registry.list_jobs())


def test_other_running_instance_follows_new_published_generation(rag_factory):
    source = manual(rag_factory)
    first, second = rag_factory(), rag_factory()
    old = second.pipeline
    source.write_text("# Response\n\nIsolate compromised hosts.", encoding="utf-8")
    first.build_index()
    second.parser.parse = Mock(side_effect=AssertionError("refresh must not parse"))
    assert "Isolate" in second.search("isolate", 1)[0]["content"]
    assert second.pipeline is not old
    assert "failed login" in old.search_rankings("failed login", 1)["parents"][0]["content"]


def test_restart_uses_last_good_generation_when_new_build_fails(rag_factory):
    source = manual(rag_factory)
    first = rag_factory()
    before = generation(first)
    source.write_text("# Replacement\n\nUpdated document.", encoding="utf-8")
    restarted = rag_factory(build=False)
    restarted.parser.parse = Mock(side_effect=RuntimeError("parser offline"))
    assert "failed login" in restarted.search("login", 1)[0]["content"]
    assert "parser offline" in restarted.last_build_error
    assert generation(restarted) == before
    assert restarted.registry.list_jobs()[0]["status"] == "failed"


def test_restart_can_recover_previous_pointer_but_never_an_unpublished_directory(rag_factory):
    source = manual(rag_factory)
    first = rag_factory()
    previous = generation(first)
    source.write_text("# Response\n\nIsolate hosts.", encoding="utf-8")
    first.build_index()
    broken = generation(first)
    (first.repository.root / broken / "faiss.index").write_bytes(b"corrupt")
    restarted = rag_factory(build=False)
    restarted.parser.parse = Mock(side_effect=RuntimeError("parser offline"))
    assert "failed login" in restarted.search("login", 1)[0]["content"]
    assert restarted._generation_id == previous
    assert "No intact" not in (restarted.last_build_error or "")


def test_restart_reconciles_abandoned_and_already_published_jobs(rag_factory):
    manual(rag_factory)
    first = rag_factory()
    current = generation(first)
    abandoned = first.registry.start_job("index", current)
    committed = first.registry.start_job("index", current)
    first.registry.update_job_output(committed, first.registry.revision, current)
    restarted = rag_factory()
    jobs = {job["job_id"]: job for job in restarted.registry.list_jobs()}
    assert jobs[abandoned]["status"] == "failed"
    assert jobs[abandoned]["error_code"] == "InterruptedBuild"
    assert jobs[committed]["status"] == "succeeded"


def test_rollback_does_not_restore_deleted_knowledge_and_survives_restart(rag_factory):
    source = manual(rag_factory)
    retriever = rag_factory()
    document = retriever.documents[0]
    old = generation(retriever)
    source.write_text("# Response\n\nIsolate compromised hosts.", encoding="utf-8")
    retriever.build_index()
    retriever.lifecycle.delete(document.document_id)
    retriever.rollback_generation(old)
    assert generation(retriever) == old
    assert retriever.search("login", 5) == []
    restarted = rag_factory()
    assert generation(restarted) == old
    assert restarted.search("login", 5) == []
    restarted.lifecycle.restore(document.document_id)
    assert "failed login" in restarted.search("login", 1)[0]["content"]


def test_missing_registry_fails_closed_instead_of_recreating_document_identities(rag_factory):
    manual(rag_factory)
    first = rag_factory()
    first.registry.path.rename(first.registry.path.with_suffix(".backup"))
    with pytest.raises(ValueError, match="registry is missing"):
        rag_factory()
    with pytest.raises(ValueError, match="registry is missing"):
        first.search("login", 1)


def test_first_batch_registry_migrates_without_changing_document_identity(tmp_path):
    import hashlib
    import sqlite3
    from app.rag.lifecycle.registry import DocumentRegistry, _SCHEMA, path_key
    from app.rag.lifecycle.service import LifecycleService
    source = tmp_path / "manual.md"
    source.write_text("immutable bytes", encoding="utf-8")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    storage = tmp_path / "storage"
    blob = storage / "sources" / digest / "source.md"
    blob.parent.mkdir(parents=True)
    blob.write_bytes(source.read_bytes())
    database = storage / "registry.db"
    with sqlite3.connect(database) as connection:
        connection.executescript(_SCHEMA)
        connection.execute("INSERT INTO documents VALUES (?, ?, ?, ?, NULL, ?, ?)",
                           ("stable-document", "path:" + path_key(source), str(source.resolve()), path_key(source), "before", "before"))
        connection.execute("INSERT INTO document_versions VALUES (?, ?, ?, ?, ?, ?, ?)",
                           ("immutable-version", "stable-document", 1, digest, str(blob.resolve()), "md", "before"))
        connection.execute("UPDATE documents SET latest_version_id = 'immutable-version'")
        connection.execute("UPDATE registry_meta SET lifecycle_revision = 7")
    service = LifecycleService(storage, DocumentRegistry(storage))
    document, version = service.import_document(source)
    assert document.document_id == "stable-document" and version.version_id == "immutable-version"
    assert service.registry.revision == 7
    assert document.deleted_at is None and document.expires_at is None
    job = service.registry.start_job("migration-test", None)
    service.registry.finish_job(job, metrics={"checked": 1})
    assert service.registry.list_jobs()[0]["metrics"] == {"checked": 1}
