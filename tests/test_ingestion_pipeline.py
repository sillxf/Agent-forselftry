"""Standalone document processing, compatibility and model-budget regression checks."""
from pathlib import Path
from shutil import copyfile
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.rag.chunking.child_chunker import ChildChunker
from app.rag.chunking.parent_chunker import ParentChunker
from app.rag.ingestion.docling_parser import DoclingParser
from app.rag.ingestion.pipeline import IngestionPipeline
from conftest import CharacterTokenizer


def test_standalone_ingestion_deduplicates_mixed_formats_without_building_an_index(rag_factory, monkeypatch):
    import app.rag.retriever as retriever_module

    monkeypatch.setattr(retriever_module, "get_model", Mock(side_effect=AssertionError("must not load a model")))
    source = rag_factory.knowledge / "a.md"
    source.write_text("# Detection\n\nRepeated failed login attempts require investigation.", encoding="utf-8")
    copyfile(source, rag_factory.knowledge / "z-copy.md")
    copyfile(Path(__file__).parent / "fixtures/rag_documents/docx/no_heading.docx",
             rag_factory.knowledge / "b.docx")
    parser = DoclingParser()
    parser.parse = Mock(wraps=parser.parse)
    tokenizer = CharacterTokenizer()
    pipeline = IngestionPipeline(parser, ParentChunker(tokenizer, 1600), ChildChunker(tokenizer, 240, 25))
    result = pipeline.run(rag_factory.knowledge)
    assert [doc.filename for doc in result.documents] == ["a.md", "b.docx"]
    assert parser.parse.call_count == 2
    assert result.parents and result.children
    assert not rag_factory.storage.exists()
    assert not list(rag_factory.knowledge.rglob("faiss.index"))
    # The existing facade must produce exactly the same records, text, ordering and IDs.
    retriever = rag_factory()
    assert result.documents == retriever.documents
    assert result.parents == list(retriever.parents.values())
    assert [child.model_dump(mode="json") for child in result.children] == retriever.store.records


def test_ingestion_empty_input_and_parser_failure_do_not_publish_an_index(tmp_path):
    parser = Mock()
    pipeline = IngestionPipeline(parser, Mock(), Mock())
    empty = pipeline.run(tmp_path)
    assert empty.documents == empty.parents == empty.children == []
    parser.parse.assert_not_called()
    source = tmp_path / "manual.pdf"
    source.write_bytes(b"invalid pdf")
    parser.parse.side_effect = RuntimeError("parser failed")
    with pytest.raises(RuntimeError, match="parser failed"):
        pipeline.run(tmp_path)
    assert list(tmp_path.iterdir()) == [source]


def test_facade_preserves_lazy_model_loading_and_effective_child_budget(rag_factory, monkeypatch):
    import app.rag.retriever as retriever_module

    source = rag_factory.knowledge / "manual.md"
    source.write_text("# Detection\n\n" + "Repeated failed login attempts. " * 12, encoding="utf-8")
    tokenizer = CharacterTokenizer()
    tokenizer.num_special_tokens_to_add = Mock(return_value=2)
    get_model = Mock(return_value=SimpleNamespace(tokenizer=tokenizer, max_seq_length=96))
    monkeypatch.setattr(retriever_module, "get_model", get_model)
    ingestion = Mock(wraps=IngestionPipeline)
    monkeypatch.setattr(retriever_module, "IngestionPipeline", ingestion)
    retriever = rag_factory(build=False, tokenizer=None, child_max_tokens=240, overlap_tokens=200)
    get_model.assert_not_called()
    assert not rag_factory.storage.exists()
    retriever.build_index()
    get_model.assert_called_once_with("test-local-v1")
    tokenizer.num_special_tokens_to_add.assert_called_once_with(pair=False)
    _, parent_chunker, child_chunker = ingestion.call_args.args
    assert parent_chunker.tokenizer is tokenizer
    assert child_chunker.max_tokens == 94
    assert child_chunker.overlap_tokens == 93
    assert all(len(row["search_text"]) <= 94 for row in retriever.store.records)
