# AI-SecOps-Agent

An AI-assisted security alert investigation system.

## Current features

- Security alert data model
- List and filter alerts by severity
- Retrieve a single alert by ID
- HTTP API tests

## Setup

Create and activate a Python virtual environment, then run:

    python -m pip install -r requirements.txt

## Start the application

    uvicorn app.main:app --reload

## Run tests

    pytest -q

## API documentation

Open http://127.0.0.1:8000/docs

## Roadmap

- Alert normalization and deduplication
- Asset and event investigation tools
- Retrieval-augmented generation
- Agent tool calling
- Workflow and ReAct comparison
- Evaluation and observability

## RAG Pipeline — first round

1. Docling parses Markdown, PDF, DOCX, XLSX, PPTX, HTML and images into shared
   document/block records, retaining headings, available page numbers, tables and pictures.
2. Section-aware parents provide context; smaller overlapping children provide retrieval
   units. Chunking uses the embedding tokenizer and counts source/section prefixes in the
   model's input budget. Tables retain column/value pairs and are grouped by whole rows.
3. Normalized embeddings use FAISS cosine retrieval. BM25+ preserves exact security
   identifiers and uses basic Chinese character/bigram tokens. RRF merges both rankings.
4. Search restores parent context and keeps source names, document/parent/chunk IDs,
   section paths, page ranges and picture paths.

`KnowledgeRetriever(build=True/False)`, `build_index()`, `search(query, k=2)` and
`/knowledge/search?q=...&k=3` remain available. Results retain `source` and `content`;
`content` is now the parent context and `chunk_content` is the matched fragment.
`matched_page_start/end` cover the child's source blocks; pageless formats use null.
The investigation prompt retains source identities and treats retrieved text as
untrusted reference data. Its analysis output schema is unchanged.

### Configuration and indexing

Install `requirements.txt`; see `.env.example` for RAG settings. Relative paths resolve
against the repository. The default embedding remains `all-MiniLM-L6-v2`; set
`RAG_EMBEDDING_MODEL=BAAI/bge-m3` to evaluate the larger multilingual candidate.
Embedding and PDF layout/OCR models may download on first use.

```powershell
# Build explicitly, or rebuild after changing knowledge in a running service:
.\.venv\Scripts\python.exe -c "from app.rag.retriever import KnowledgeRetriever; KnowledgeRetriever(build=False).build_index()"

# Run offline unit/integration tests without an LLM service:
.\.venv\Scripts\python.exe -m pytest -q
```

`build=False` loads/builds on the first search. Initialization reuses an index when
source hashes, model and chunk settings match. A running process retains its in-memory
index until explicit rebuild or restart. Identical files are indexed once.

Generated files live in the Git-ignored `app/storage/` directory:

```text
parsed/<checksum>.json + .md       # Docling exports
images/<checksum>/...             # extracted pictures / original image inputs
indexes/current.json              # active generation and pipeline settings
indexes/<generation>/
  faiss.index
  chunks.jsonl
  metadata.db                     # document / parent / child relationships
```

A generation is published after its files are saved. Old generations are retained;
automatic cleanup, index repair and multi-user permissions are outside this round.
Index files are local, trusted application data.

### Validation and next steps

Tests focus on format parsing, page/section and table preservation, token windows,
hybrid retrieval, persistence/rebuild, API compatibility and the offline investigation
flow. Markdown/Office/HTML parsing uses real Docling; PDF/picture mapping uses a small
converter fixture. Real scanned-PDF/image OCR still needs representative-file acceptance
testing. Set `RAG_OCR_ENABLED=false` to disable OCR, not PDF layout/table processing.

Deferred: cross-page continuation inference/merging, inferred headings, VLM image
understanding, image vectors, reranking, neighbour expansion and report-level citation
evaluation. Same-section page blocks already share parent context. A single oversized
table row stays intact in its parent, while children remain token-bounded. Legacy
binary Office files, Qdrant and knowledge graphs are not introduced.

## Example Investigation Flow
输入：
AL-001

系统：
1. Load alert

2. Calculate risk

3. Retrieve security knowledge

4. Build investigation context

5. Generate analysis

输出：
Attack:
Brute Force

Evidence:
Multiple failed login attempts

Recommendation:
Block IP
Enable MFA
Investigate account