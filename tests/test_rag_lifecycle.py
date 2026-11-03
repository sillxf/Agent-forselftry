"""Managed identity migration: immutable inputs, version isolation and frozen labels."""
import hashlib
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import Mock

import pytest

from app.rag.indexing.pipeline import IndexSnapshot
from app.rag.indexing.vector_store import FaissVectorStore
from app.rag.lifecycle.registry import DocumentRegistry
from app.rag.lifecycle.service import LifecycleService
from evaluation.rag.dataset import Dataset, Evidence
from evaluation.rag.runner import derive_qrels, evaluation_units, map_evidence, run_benchmark


def test_registry_is_lazy_and_empty_reads_do_not_create_storage(tmp_path):
    root = tmp_path / "not-created"
    registry = DocumentRegistry(root)
    LifecycleService(root, registry)
    assert registry.revision == 0
    assert registry.list_documents() == registry.list_versions("missing") == []
    assert not root.exists()


def test_registration_is_persistent_idempotent_and_preserves_source_versions(tmp_path):
    source = tmp_path / "manual.md"
    source.write_text("first content", encoding="utf-8")
    service = LifecycleService(tmp_path / "storage")
    document, first = service.import_document(source)
    assert document.document_id != first.content_hash
    assert document.latest_version_id == first.version_id
    assert first.version_number == 1
    assert Path(first.source_blob_path).read_text(encoding="utf-8") == "first content"
    revision = service.registry.revision
    again = LifecycleService(tmp_path / "storage")
    assert again.import_document(source) == (document, first)
    assert again.registry.revision == revision
    source.write_text("second content", encoding="utf-8")
    changed, second = service.import_document(source)
    assert changed.document_id == document.document_id
    assert second.version_number == 2 and second.version_id != first.version_id
    assert Path(first.source_blob_path).read_text(encoding="utf-8") == "first content"
    assert service.registry.revision == revision + 1
    source.write_text("first content", encoding="utf-8")
    restored, version = service.import_document(source)
    assert restored.latest_version_id == first.version_id and version == first
    assert service.registry.list_versions(document.document_id) == [first, second]
    assert service.registry.revision == revision + 2


def test_equal_content_is_shared_without_merging_logical_documents(tmp_path):
    a, b = tmp_path / "a.md", tmp_path / "b.md"
    a.write_text("same bytes", encoding="utf-8")
    b.write_bytes(a.read_bytes())
    service = LifecycleService(tmp_path / "storage")
    doc_a, version_a = service.import_document(a)
    doc_b, version_b = service.import_document(b)
    assert doc_a.document_id != doc_b.document_id
    assert version_a.version_id != version_b.version_id
    assert version_a.source_blob_path == version_b.source_blob_path
    assert len(service.registry.list_documents()) == 2


def test_external_source_identity_can_explicitly_move_without_merging_a_path(tmp_path):
    a, b = tmp_path / "a.md", tmp_path / "b.md"
    a.write_text("same bytes", encoding="utf-8")
    b.write_bytes(a.read_bytes())
    service = LifecycleService(tmp_path / "storage")
    document, version = service.import_document(a, source_id="upstream-42")
    moved, moved_version = service.import_document(b, source_id="upstream-42")
    assert moved.document_id == document.document_id and moved_version == version
    assert moved.source_path == str(b.resolve())
    assert service.import_document(b) == (moved, version)
    with pytest.raises(ValueError, match="different document"):
        service.import_document(b, source_id="upstream-43")
    assert len(service.registry.list_documents()) == 1


def test_explicit_rename_preserves_version_but_invalidates_filename_derived_assets(tmp_path):
    a, b = tmp_path / "manual.md", tmp_path / "renamed.md"
    a.write_text("content", encoding="utf-8")
    service = LifecycleService(tmp_path / "storage")
    document, version = service.import_document(a)
    before = service.processing_document(document, version, {"chunking": 1})
    a.rename(b)
    moved = service.rename(document.document_id, b)
    assert moved.document_id == document.document_id
    assert service.import_document(b) == (moved, version)
    after = service.processing_document(moved, version, {"chunking": 1})
    assert before.version_id == after.version_id
    assert before.artifact_id != after.artifact_id
    assert before.source_blob_path == after.source_blob_path
    assert len(service.registry.list_documents()) == 1


def test_rename_conflict_rolls_back_registry_revision_and_identity(tmp_path):
    a, b = tmp_path / "a.md", tmp_path / "b.md"
    a.write_text("same content", encoding="utf-8")
    b.write_bytes(a.read_bytes())
    service = LifecycleService(tmp_path / "storage")
    document, _ = service.import_document(a)
    service.import_document(b)
    revision = service.registry.revision
    with pytest.raises(sqlite3.IntegrityError):
        service.rename(document.document_id, b)
    assert service.registry.revision == revision
    assert service.registry.get_document(document.document_id) == document
    b.write_text("different", encoding="utf-8")
    with pytest.raises(ValueError, match="same content"):
        service.rename(document.document_id, b)
    assert service.registry.revision == revision


def test_changed_input_and_corrupt_blob_do_not_advance_registry(tmp_path):
    source = tmp_path / "manual.md"
    source.write_text("original", encoding="utf-8")
    service = LifecycleService(tmp_path / "storage")
    with pytest.raises(ValueError, match="Source changed"):
        service.import_document(source, expected_hash="0" * 64)
    assert service.registry.revision == 0
    assert not service.registry.path.exists()
    assert list(service.sources.iterdir()) == []
    document, version = service.import_document(source)
    revision = service.registry.revision
    Path(version.source_blob_path).write_text("corrupt", encoding="utf-8")
    with pytest.raises(ValueError, match="corrupt"):
        service.import_document(source)
    assert service.registry.revision == revision
    assert service.registry.get_document(document.document_id) == document
    assert all(path.is_dir() for path in service.sources.iterdir())


def test_concurrent_imports_are_idempotent_and_publish_complete_source_bytes(tmp_path):
    source = tmp_path / "manual.md"
    source.write_bytes(b"immutable source" * 1000)
    storage = tmp_path / "storage"
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: LifecycleService(storage).import_document(source), range(4)))
    assert all(result == results[0] for result in results)
    registry = DocumentRegistry(storage)
    assert registry.revision == 1
    assert len(registry.list_versions(results[0][0].document_id)) == 1
    blob = Path(results[0][1].source_blob_path)
    assert blob.read_bytes() == source.read_bytes()
    assert hashlib.sha256(blob.read_bytes()).hexdigest() == results[0][1].content_hash


def test_rebuild_update_and_rechunk_keep_correct_identity_boundaries(rag_factory):
    source = rag_factory.knowledge / "manual.md"
    source.write_text("# Detection\n\nRepeated failed login attempts.", encoding="utf-8")
    retriever = rag_factory()
    first = retriever.documents[0]
    first_records = list(retriever.store.records)
    retriever.build_index()
    assert retriever.documents[0] == first
    assert retriever.store.records == first_records
    rechunked = rag_factory(child_max_tokens=120)
    second = rechunked.documents[0]
    assert (first.document_id, first.version_id) == (second.document_id, second.version_id)
    assert first.artifact_id != second.artifact_id
    assert {item["chunk_id"] for item in first_records}.isdisjoint(
        item["chunk_id"] for item in rechunked.store.records)
    assert rechunked.registry.revision == 1
    pointer = rechunked.repository.root / "current.json"
    previous_generation = json.loads(pointer.read_text(encoding="utf-8"))["generation"]
    source.write_text("# Response\n\nIsolate compromised hosts.", encoding="utf-8")
    rechunked.build_index()
    third = rechunked.documents[0]
    assert third.document_id == second.document_id and third.version_id != second.version_id
    assert third.artifact_id != second.artifact_id
    old = rechunked.repository.load_generation(previous_generation)
    assert old.documents[0] == second
    assert all(item["version_id"] == second.version_id for item in old.store.records)
    assert all(item["version_id"] == third.version_id for item in rechunked.store.records)
    assert rechunked.retrieval_modes == ("hybrid",)


def test_unrelated_document_assets_do_not_change_when_another_document_updates(rag_factory):
    a, b = rag_factory.knowledge / "a.md", rag_factory.knowledge / "b.md"
    a.write_text("# A\n\nFirst document.", encoding="utf-8")
    b.write_text("# B\n\nSecond document.", encoding="utf-8")
    retriever = rag_factory()
    original = next(document for document in retriever.documents if document.filename == "a.md")
    records = [item for item in retriever.store.records if item["document_id"] == original.document_id]
    b.write_text("# B\n\nUpdated second document.", encoding="utf-8")
    retriever.build_index()
    assert next(document for document in retriever.documents if document.filename == "a.md") == original
    assert [item for item in retriever.store.records if item["document_id"] == original.document_id] == records


def test_failed_new_version_build_leaves_old_served_generation_intact(rag_factory):
    source = rag_factory.knowledge / "manual.md"
    source.write_text("# Detection\n\nFailed login attempts.", encoding="utf-8")
    retriever = rag_factory()
    served = retriever.documents[0]
    pointer = retriever.repository.root / "current.json"
    before = pointer.read_bytes()
    original_embed = retriever.embedding_fn
    source.write_text("# Response\n\nRestore clean backups.", encoding="utf-8")
    retriever.embedding_fn = Mock(side_effect=RuntimeError("encode failed"))
    with pytest.raises(RuntimeError, match="encode failed"):
        retriever.build_index()
    assert pointer.read_bytes() == before
    assert retriever.documents[0] == served
    latest = retriever.registry.get_document(served.document_id)
    assert latest.latest_version_id != served.version_id
    retriever.embedding_fn = original_embed
    retriever.build_index()
    assert retriever.documents[0].version_id == latest.latest_version_id
    assert len(retriever.registry.list_versions(served.document_id)) == 2


@pytest.mark.parametrize("asset", ["chunks.jsonl", "faiss.index", "metadata.db"])
def test_generation_manifest_rejects_corrupt_assets_before_load(rag_factory, asset):
    (rag_factory.knowledge / "manual.md").write_text("# A\n\nEvidence.", encoding="utf-8")
    retriever = rag_factory()
    generation = json.loads((retriever.repository.root / "current.json").read_text(encoding="utf-8"))["generation"]
    root = retriever.repository.root / generation
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["documents"][0]["version_id"] == retriever.documents[0].version_id
    assert manifest["counts"]["children"] == len(retriever.store.records)
    (root / asset).write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="checksum mismatch"):
        retriever.repository.load_generation(generation)


def test_mixed_version_metadata_cannot_be_saved_or_published(rag_factory):
    (rag_factory.knowledge / "manual.md").write_text("# A\n\nEvidence.", encoding="utf-8")
    retriever = rag_factory()
    pointer = retriever.repository.root / "current.json"
    before = pointer.read_bytes()
    parent = next(iter(retriever.parents.values())).model_copy(update={"version_id": "wrong"})
    snapshot = IndexSnapshot(retriever.store, retriever.documents, [parent])
    with pytest.raises(ValueError, match="different document version"):
        retriever.repository.save(snapshot, retriever._signature()[0])
    assert pointer.read_bytes() == before
    store = Mock(records=[dict(item, artifact_id="wrong") for item in retriever.store.records])
    snapshot = IndexSnapshot(store, retriever.documents, list(retriever.parents.values()))
    with pytest.raises(ValueError, match="different document version"):
        retriever.repository.save(snapshot, retriever._signature()[0])
    store.save.assert_not_called()


def test_vector_store_rejects_mismatched_vector_and_record_counts(tmp_path):
    store = FaissVectorStore(2)
    store.add([[1, 0]], [{"chunk_id": "one"}])
    store.save(tmp_path)
    (tmp_path / "chunks.jsonl").write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="Vector count"):
        FaissVectorStore.load(tmp_path)


def test_frozen_checksum_labels_still_resolve_against_managed_index(rag_factory, tmp_path):
    source = rag_factory.knowledge / "manual.md"
    source.write_text("# Detection\n\nRepeated failed login attempts.", encoding="utf-8")
    retriever = rag_factory()
    document = retriever.documents[0]
    block = next(block for parent in retriever.parents.values() for block in parent.blocks if "failed login" in block.text)
    evidence = Evidence(evidence_id="logins", document_id=document.checksum, source=document.filename,
                        source_block_ids=[block.block_id], section_path=block.section_path,
                        page_number=block.page_number, page_end=block.page_end,
                        text_quote="failed login", relevance_grade=3)
    data = tmp_path / "labels"
    data.mkdir()
    question = dict(id="q1", question="failed login", category="test", difficulty="easy", language="en",
                    question_type="english", answerable=True, relevant_evidence=[evidence.model_dump()],
                    expected_answer="Repeated failed login attempts", review_status="pending",
                    rationale="Frozen source hash, source block and quote identify the evidence.")
    (data / "questions.jsonl").write_text(json.dumps(question), encoding="utf-8")
    (data / "dataset.json").write_text(json.dumps(dict(schema_version=1, version="test",
                                                      documents_dir=str(rag_factory.knowledge))), encoding="utf-8")
    (rag_factory.knowledge.parent / "manifest.json").write_text(json.dumps(dict(version="test", documents=[
        dict(file="manual.md", sha256=document.checksum)])), encoding="utf-8")
    dataset = Dataset(data / "questions.jsonl")
    dataset.validate_corpus()
    dataset.validate_index(retriever)
    units = evaluation_units(retriever)
    assert all(derive_qrels(dataset.questions[0], units).values())
    rows = run_benchmark(dataset, retriever, top_k=5)
    assert rows[0]["error"] is None
    assert rows[0]["child_metrics"]["recall"] == rows[0]["parent_metrics"]["recall"] == 1
    result = units["children"][0]
    assert map_evidence(result, [evidence]) == ["logins"]
    assert map_evidence(dict(result, source_name="other.md"), [evidence]) == []
    assert map_evidence(dict(result, source_checksum="different"), [evidence]) == []
    assert map_evidence(dict(result, content="unrelated"), [evidence]) == []


def test_managed_ingestion_uses_frozen_bytes_even_after_original_source_disappears(tmp_path):
    from app.rag.chunking.child_chunker import ChildChunker
    from app.rag.chunking.parent_chunker import ParentChunker
    from app.rag.ingestion.docling_parser import DoclingParser
    from app.rag.ingestion.pipeline import IngestionPipeline
    from conftest import CharacterTokenizer

    source = tmp_path / "original.md"
    source.write_text("# Detection\n\nOriginal evidence.", encoding="utf-8")
    service = LifecycleService(tmp_path / "storage")
    document, version = service.import_document(source)
    record = service.processing_document(document, version, {"revision": 1})
    source.unlink()
    pipeline = IngestionPipeline(DoclingParser(), ParentChunker(CharacterTokenizer()), ChildChunker(CharacterTokenizer()))
    result = pipeline.run(tmp_path, documents=[record])
    assert result.documents[0].filename == "original.md"
    assert all(block.document_id == document.document_id for parent in result.parents for block in parent.blocks)
    assert any("Original evidence" in child.content for child in result.children)
    assert all(child.source_name == "original.md" for child in result.children)


def test_managed_image_placeholders_keep_original_display_name(rag_factory):
    from types import SimpleNamespace
    from app.rag.ingestion.docling_parser import DoclingParser

    fixture = Path(__file__).parent / "fixtures/rag_documents/images/no_ocr.png"
    (rag_factory.knowledge / "screenshot.png").write_bytes(fixture.read_bytes())
    converter = Mock()
    converter.convert.return_value = SimpleNamespace(status="success", document=SimpleNamespace(
        iterate_items=lambda **kwargs: [], export_to_markdown=lambda: "", export_to_dict=lambda: {}))
    parser = DoclingParser(converter=converter, image_dir=rag_factory.storage / "images", ocr_enabled=False)
    retriever = rag_factory(parser=parser)
    assert any("Image in screenshot.png" in item["content"] for item in retriever.store.records)
    assert not any("Image in source.png" in item["content"] for item in retriever.store.records)


def test_managed_generation_requires_its_manifest_even_for_empty_indexes(rag_factory):
    retriever = rag_factory()
    pointer = json.loads((retriever.repository.root / "current.json").read_text(encoding="utf-8"))
    (retriever.repository.root / pointer["generation"] / "manifest.json").unlink()
    with pytest.raises(ValueError, match="missing its manifest"):
        retriever.repository.load_current(pointer["signature"])


def test_document_cli_lists_versions_and_explicitly_maps_a_rename(tmp_path):
    import subprocess
    import sys

    root = Path(__file__).resolve().parents[1]
    storage = tmp_path / "storage"
    command = [sys.executable, str(root / "scripts/rag_documents.py"), "--storage-dir", str(storage)]
    output = subprocess.run([*command, "list"], capture_output=True, text=True, check=True)
    assert json.loads(output.stdout) == []
    assert not storage.exists()
    source = tmp_path / "a.md"
    source.write_text("Content", encoding="utf-8")
    service = LifecycleService(storage)
    document, version = service.import_document(source)
    output = subprocess.run([*command, "versions", document.document_id], capture_output=True, text=True, check=True)
    assert json.loads(output.stdout)[0]["version_id"] == version.version_id
    moved = source.rename(tmp_path / "b.md")
    output = subprocess.run([*command, "rename", document.document_id, str(moved)], capture_output=True, text=True, check=True)
    result = json.loads(output.stdout)
    assert result["document_id"] == document.document_id
    assert result["latest_version_id"] == version.version_id
    assert service.registry.get_document(document.document_id).source_path == str(moved.resolve())


def test_identity_migration_preserves_legacy_hybrid_tie_breaks(rag_factory):
    from app.rag.chunking.child_chunker import ChildChunker
    from app.rag.chunking.parent_chunker import ParentChunker
    from app.rag.ingestion.docling_parser import DoclingParser
    from app.rag.ingestion.pipeline import IngestionPipeline
    from app.rag.indexing.pipeline import IndexingPipeline
    from conftest import CharacterTokenizer, LocalEmbedder
    for index, topic in enumerate(("login", "malware", "network")):
        (rag_factory.knowledge / f"{index}.md").write_text(f"# {topic}\n\nEvidence for {topic} response.", encoding="utf-8")
    managed = rag_factory()
    tokenizer = CharacterTokenizer()
    result = IngestionPipeline(DoclingParser(), ParentChunker(tokenizer, 1600), ChildChunker(tokenizer, 240, 25)).run(rag_factory.knowledge)
    snapshot = IndexingPipeline(LocalEmbedder()).build(result)
    legacy = rag_factory(build=False)
    legacy.attach_index(snapshot.store, snapshot.documents, {parent.parent_id: parent for parent in snapshot.parents})
    for query in ("unknown", "response", "login", "malware", "network"):
        before = legacy.search_rankings(query, 5)
        after = managed.search_rankings(query, 5)
        assert [item["chunk_id"] for item in before["children"]] == [item["retrieval_key"] for item in after["children"]]
        assert [item["content"] for item in before["parents"]] == [item["content"] for item in after["parents"]]
