from unittest.mock import Mock

from app.rag.retriever import tokenize


def add_manual(factory):
    (factory.knowledge / "manual.md").write_text(
        "# Security manual\n\n## Detection\n\nMultiple failed login attempts indicate brute force.\n\n"
        "Block suspicious IP and enable MFA.\n\n## Malware\n\nIsolate compromised systems.", encoding="utf-8")


def test_search_restores_parent_and_keeps_api_compatible(rag_factory, monkeypatch):
    from fastapi.testclient import TestClient
    import app.main as main

    add_manual(rag_factory)
    retriever = rag_factory()
    results = retriever.search("failed login attempts", k=2)
    hit = results[0]
    assert hit["source"] == "manual.md"
    assert "failed login" in hit["content"] and "enable MFA" in hit["content"]
    assert hit["chunk_id"] and hit["parent_id"] and hit["document_id"]
    assert hit["page_start"] is None
    assert len({item["parent_id"] for item in results}) == len(results)
    monkeypatch.setattr(main, "knowledge_retriever", retriever)
    response = TestClient(main.app).get("/knowledge/search", params={"q": "failed login attempts", "k": 2})
    assert response.status_code == 200
    assert response.json()["results"] == results


def test_persistence_reuses_index_and_changed_sources_rebuild(rag_factory):
    add_manual(rag_factory)
    first = rag_factory()
    expected = first.search("failed login", 2)
    second = rag_factory(build=False)
    second.parser.parse = Mock(side_effect=AssertionError("must load existing index"))
    assert second.search("failed login", 2) == expected
    assert second.embedding_fn.calls == [["failed login"]]

    (rag_factory.knowledge / "manual.md").write_text("Updated response protocol", encoding="utf-8")
    third = rag_factory()
    assert third.documents[0].checksum != first.documents[0].checksum
    assert "Updated response" in third.search("response")[0]["content"]


def test_bm25_recalls_identifiers_when_dense_vectors_are_identical(rag_factory):
    identifiers = "CVE-2025-12345 192.168.1.10 R001"
    (rag_factory.knowledge / "match.md").write_text(f"# Rules\n\n{identifiers} mitigation response", encoding="utf-8")
    (rag_factory.knowledge / "other.md").write_text("# Other\n\nUnrelated security guideline", encoding="utf-8")
    retriever = rag_factory(embedding_fn=lambda texts: [[1.0, 0.0] for _ in texts])
    for identifier in identifiers.split():
        hit = retriever.search(identifier, 1)[0]
        assert identifier in hit["content"] and hit["sparse_score"] > 0
    assert {"中文", "告警", "cve-2025-12345"} <= set(tokenize("中文告警 CVE-2025-12345"))


def test_identical_source_files_are_indexed_once(rag_factory):
    add_manual(rag_factory)
    (rag_factory.knowledge / "copy.md").write_bytes((rag_factory.knowledge / "manual.md").read_bytes())
    assert len(rag_factory().documents) == 1
