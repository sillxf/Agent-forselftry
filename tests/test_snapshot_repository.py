"""Legacy format compatibility and prepare-before-publish failure guarantees."""
import json
from pathlib import Path
from shutil import copytree
from unittest.mock import Mock

import pytest

from app.rag.indexing.snapshot_repository import SnapshotRepository
from app.rag.indexing.vector_store import FaissVectorStore


ROOT = Path(__file__).resolve().parents[1]


def test_legacy_generation_load_save_and_publish_keep_existing_format_and_old_versions(tmp_path):
    repository = SnapshotRepository(tmp_path)
    assert repository.load_current({}) is None
    baseline = ROOT / "evaluation_results/baselines/2026-11-01_security_v1_balanced_minilm"
    config = json.loads((baseline / "hybrid/config.json").read_text(encoding="utf-8"))
    signature = config["index"]["signature"]
    legacy = repository.root / "legacy-generation"
    copytree(baseline / "index_snapshot", legacy)
    pointer = repository.root / "current.json"
    pointer.write_text(json.dumps(dict(generation=legacy.name, signature=signature)), encoding="utf-8")
    original_pointer = pointer.read_bytes()
    snapshot = repository.load_current(signature)
    assert len(snapshot.documents) == 21
    assert len(snapshot.parents) == 70
    assert len(snapshot.store.records) == 301
    assert repository.load_current(dict(signature, model="different")) is None
    saved = repository.save(snapshot, signature)
    assert pointer.read_bytes() == original_pointer  # save is never an implicit publish
    assert (repository.root / saved.generation / "faiss.index").read_bytes() == (legacy / "faiss.index").read_bytes()
    assert (repository.root / saved.generation / "chunks.jsonl").read_bytes() == (legacy / "chunks.jsonl").read_bytes()
    repository.publish(saved)
    published = json.loads(pointer.read_text(encoding="utf-8"))
    assert published["generation"] == saved.generation and published["signature"] == signature
    assert repository.publications()[0]["publication_id"] == published["publication_id"]
    restored = repository.load_current(signature)
    assert restored.documents == snapshot.documents
    assert restored.parents == snapshot.parents
    assert restored.store.records == snapshot.store.records
    assert repository.load_generation(legacy.name).store.records == snapshot.store.records
    assert (legacy / "metadata.db").exists()


@pytest.mark.parametrize("failure", ["vector_save", "metadata_save", "query_prepare", "publish"])
def test_prepublication_failures_keep_old_pointer_and_in_memory_query_snapshot(rag_factory, monkeypatch, failure):
    import app.rag.indexing.snapshot_repository as repository_module
    import app.rag.retriever as retriever_module

    source = rag_factory.knowledge / "manual.md"
    source.write_text("# Detection\n\nRepeated failed login attempts.", encoding="utf-8")
    retriever = rag_factory()
    old_store, old_pipeline = retriever.store, retriever.pipeline
    old_documents, old_parents = retriever.documents, retriever.parents
    expected = retriever.search("failed login", 2)
    pointer = retriever.repository.root / "current.json"
    previous = pointer.read_bytes()
    current = json.loads(previous)
    source.write_text("# Response\n\nIsolate compromised hosts and restore clean backups.", encoding="utf-8")
    with monkeypatch.context() as patcher:
        if failure == "vector_save":
            patcher.setattr(FaissVectorStore, "save", Mock(side_effect=RuntimeError("vector save failed")))
        elif failure == "metadata_save":
            patcher.setattr(repository_module.sqlite3, "connect", Mock(side_effect=RuntimeError("metadata save failed")))
        elif failure == "query_prepare":
            patcher.setattr(retriever_module.RetrievalPipeline, "from_index", Mock(side_effect=RuntimeError("query prepare failed")))
        else:
            original_replace = Path.replace

            def fail_pointer_replace(path, target):
                if path.name.startswith(".current-"):
                    raise RuntimeError("pointer publish failed")
                return original_replace(path, target)

            patcher.setattr(Path, "replace", fail_pointer_replace)
        with pytest.raises(RuntimeError, match="failed"):
            retriever.build_index()
    assert pointer.read_bytes() == previous
    assert retriever.store is old_store and retriever.pipeline is old_pipeline
    assert retriever.documents is old_documents and retriever.parents is old_parents
    assert retriever.search("failed login", 2) == expected
    restored = retriever.repository.load_current(current["signature"])
    assert restored.store.records == old_store.records
    assert restored.documents == old_documents
    assert (retriever.repository.root / current["generation"] / "metadata.db").exists()


def test_successful_build_prepares_query_before_publishing_and_only_then_switches_memory(rag_factory, monkeypatch):
    source = rag_factory.knowledge / "manual.md"
    source.write_text("# Detection\n\nRepeated failed login attempts.", encoding="utf-8")
    retriever = rag_factory()
    old_store, old_pipeline = retriever.store, retriever.pipeline
    pointer = retriever.repository.root / "current.json"
    previous = pointer.read_bytes()
    events = []
    save = retriever.repository.save
    prepare = retriever._prepare_pipeline
    publish = retriever.repository.publish
    activate = retriever._activate_index

    def save_new(snapshot, signature):
        saved = save(snapshot, signature)
        assert pointer.read_bytes() == previous
        assert (retriever.repository.root / saved.generation / "metadata.db").exists()
        events.append("saved")
        return saved

    def prepare_new(store, parents, model_name, **options):
        assert pointer.read_bytes() == previous
        assert retriever.store is old_store
        prepared = prepare(store, parents, model_name, **options)
        events.append("prepared")
        return prepared

    def publish_new(saved):
        assert events == ["saved", "prepared"]
        assert retriever.store is old_store and retriever.pipeline is old_pipeline
        publish(saved)
        assert json.loads(pointer.read_text(encoding="utf-8"))["generation"] == saved.generation
        events.append("published")

    def activate_new(store, documents, parents, pipeline, model_name):
        assert events == ["saved", "prepared", "published"]
        assert retriever.store is old_store
        activate(store, documents, parents, pipeline, model_name)
        events.append("activated")

    monkeypatch.setattr(retriever.repository, "save", save_new)
    monkeypatch.setattr(retriever, "_prepare_pipeline", prepare_new)
    monkeypatch.setattr(retriever.repository, "publish", publish_new)
    monkeypatch.setattr(retriever, "_activate_index", activate_new)
    source.write_text("# Response\n\nIsolate compromised hosts.", encoding="utf-8")
    retriever.build_index()
    assert events == ["saved", "prepared", "published", "activated"]
    assert retriever.store is not old_store
    assert retriever.pipeline.dense.store is retriever.store
    assert retriever.pipeline.sparse.records is retriever.store.records
    assert retriever.pipeline.context_builder.parents is retriever.parents
    assert "Isolate" in retriever.search("isolate", 1)[0]["content"]
    reloaded = rag_factory(build=False)
    reloaded.parser.parse = Mock(side_effect=AssertionError("must reuse the published generation"))
    assert reloaded.search("isolate", 1) == retriever.search("isolate", 1)
