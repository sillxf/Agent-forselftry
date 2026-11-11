from app.rag.chunking.child_chunker import ChildChunker
from app.rag.chunking.parent_chunker import ParentChunker
from app.rag.chunking.text import split_text
from app.rag.models import ContentBlock, DocumentRecord
from conftest import CharacterTokenizer


def document():
    return DocumentRecord(document_id="doc", filename="manual.pdf", file_type="pdf", source_path="manual.pdf", checksum="abc")


def test_parent_preserves_section_boundaries_and_cross_page_evidence():
    blocks = [ContentBlock(document_id="doc", block_type="paragraph", text=text, page_number=page, section_path=[section])
              for text, page, section in [("Rule starts here,", 4, "Detection"),
                                          ("and continues here.", 5, "Detection"),
                                          ("Separate topic", 6, "Response")]]
    parents = ParentChunker(CharacterTokenizer()).split(blocks, document())
    assert len(parents) == 2
    assert parents[0].page_start == 4 and parents[0].page_end == 5
    assert "Rule starts" in parents[0].content and "continues" in parents[0].content
    children = ChildChunker(CharacterTokenizer(), 120, 10).split(parents[0], "manual.pdf", "pdf")
    assert children[0].parent_id == parents[0].parent_id
    assert children[0].page_start == 4 and children[0].page_end == 5


def test_token_windows_keep_unicode_overlap_and_embedding_budget():
    tokenizer = CharacterTokenizer()
    text = "中英文安全处置规则" * 20
    pieces = list(split_text(text, tokenizer, 30, 7))
    assert pieces[0] + "".join(piece[7:] for piece in pieces[1:]) == text
    block = ContentBlock(document_id="doc", block_type="paragraph", text=text)
    parent = ParentChunker(tokenizer).split([block], document())[0]
    children = ChildChunker(tokenizer, 100, 10).split(parent, "manual.pdf")
    assert len(children) > 1
    assert all(len(child.search_text) <= 100 for child in children)


def test_large_tables_keep_rows_columns_and_caption():
    rows = [{"Rule ID": f"R{i:03}", "Severity": "High"} for i in range(8)]
    table = ContentBlock(document_id="doc", block_type="table", text="Production rules",
                         caption="Production rules", table_columns=["Rule ID", "Severity"], table_data=rows)
    tokenizer = CharacterTokenizer()
    parents = ParentChunker(tokenizer, max_tokens=100).split([table], document())
    assert len(parents) > 1
    assert all("Production rules" in parent.content for parent in parents)
    children = [c for p in parents for c in ChildChunker(tokenizer, 120, 10).split(p, "rules.pdf")]
    assert [row for child in children for row in child.table_data] == rows
    assert all("Rule ID:" in child.content and "Severity:" in child.content for child in children)
