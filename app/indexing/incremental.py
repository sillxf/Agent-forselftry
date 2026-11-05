"""Document change planning, copy-on-write FAISS and incremental BM25 publication assets."""

from importlib.metadata import version as package_version
from pathlib import Path

import numpy as np

from app.ingestion.chunking.child_chunker import ChildChunker
from app.ingestion.chunking.parent_chunker import ParentChunker
from app.indexing.embedding_cache import CachedEmbedder
from app.indexing.pipeline import IndexSnapshot, IndexingPipeline
from app.ingestion.pipeline import IngestionPipeline, IngestionResult
from app.retrieval.strategies.sparse import SparseRetriever


def assemble(owner, signature, files, *, full=False):
    entries = {
        str(p.resolve()): item
        for p, item in zip(files, signature["files"], strict=True)
    }
    for path in files:
        existing = owner.registry.lookup_path(path)
        if path.is_file() and (existing is None or existing.deleted_at is None):
            owner.lifecycle.import_document(
                path, expected_hash=entries[str(path.resolve())]["checksum"]
            )
    sources, revision = owner.registry.capture_sources(files)
    signature = dict(signature, lifecycle_revision=revision)
    previous = None
    try:
        published = owner.repository.load_published()
        if published:
            previous, pointer = published
    except (ValueError, OSError):
        pass  # An explicit rebuild repairs unusable derived assets, never source history.
    tokenizer, budget = owner.tokenizer, owner.child_max_tokens
    if sources and tokenizer is None:
        tokenizer, model_limit = owner.embedding_resolver(
            signature["model"]
        ).tokenizer_and_limit()
        budget = min(
            budget, model_limit - tokenizer.num_special_tokens_to_add(pair=False)
        )
    processing = {
        k: v
        for k, v in signature.items()
        if k not in {"files", "lifecycle_revision", "embedding_cache_revision"}
    }
    processing["effective_child_tokens"] = budget
    documents = []
    for document, version in sources:
        if (
            not document.selected_version_id
            and version.content_hash
            != entries[str(Path(document.source_path).resolve())]["checksum"]
        ):
            raise ValueError("Source version changed while freezing build inputs")
        record = owner.lifecycle.processing_document(document, version, processing)
        record.lifecycle_state = {
            "effective_at": document.effective_at,
            "expires_at": document.expires_at,
            "deleted_at": document.deleted_at,
        }
        documents.append(record)
    # A changed embedding space/revision or unsupported custom backend must rebuild vectors.
    compatible = (
        not full
        and previous is not None
        and hasattr(previous.store, "updated")
        and owner.store_factory is type(previous.store)
        and pointer["signature"].get("version") == signature["version"]
        and pointer["signature"].get("model") == signature["model"]
        and pointer["signature"].get("embedding_cache_revision")
        == signature["embedding_cache_revision"]
    )
    old_documents = {d.document_id: d for d in previous.documents} if compatible else {}
    reused = {
        d.document_id
        for d in documents
        if d.document_id in old_documents
        and d.artifact_id == old_documents[d.document_id].artifact_id
    }
    pending = [d for d in documents if d.document_id not in reused]
    result = IngestionResult()
    ingestion = None
    if pending:
        owner.progress("parsing_and_chunking")
        ingestion = IngestionPipeline(
            owner.parser,
            ParentChunker(tokenizer, owner.parent_max_tokens),
            ChildChunker(tokenizer, budget, min(owner.overlap_tokens, budget - 1)),
            cache_dir=owner.storage_dir / "artifacts" if owner.cache_enabled else None,
            progress=owner.progress,
        )
        result = ingestion.run(owner.knowledge_dir, documents=pending)
    parsed_documents = {d.document_id: d for d in result.documents}
    documents = [
        parsed_documents.get(
            d.document_id,
            d.model_copy(update={"title": old_documents[d.document_id].title})
            if d.document_id in reused
            else d,
        )
        for d in documents
    ]
    embed = owner._embed()
    cached = None
    if owner.cache_enabled:
        cached = CachedEmbedder(
            embed,
            owner.storage_dir / "embedding_cache",
            {
                "model": signature["model"],
                "cache_revision": owner.embedding_cache_revision,
                "sentence_transformers": package_version("sentence-transformers"),
                "transformers": package_version("transformers"),
            },
        )
        embed = cached
    owner.progress("embedding_and_indexing")
    new_records = [c.model_dump(mode="json") for c in result.children]
    retained = (
        [r for r in previous.store.records if r["document_id"] in reused]
        if compatible
        else []
    )
    if compatible and (retained or not new_records):
        remove = {
            r["chunk_id"]
            for r in previous.store.records
            if r["document_id"] not in reused
        }
        vectors = (
            np.asarray(embed([r["search_text"] for r in new_records]), dtype="float32")
            if new_records
            else []
        )
        if new_records and vectors.shape[1] != previous.store.dimension:
            raise ValueError(
                "Embedding dimensions changed; use an explicit full rebuild"
            )
        store = previous.store.updated(remove, vectors, new_records)
        parents = [
            p for p in previous.parents if p.document_id in reused
        ] + result.parents
        sparse = (previous.sparse or SparseRetriever(previous.store.records)).updated(
            store.records
        )
    else:
        built = IndexingPipeline(embed, owner.store_factory).build(result)
        store, parents = built.store, built.parents
        sparse = SparseRetriever(store.records)
        compatible = False
    snapshot = IndexSnapshot(store, documents, parents, sparse=sparse)
    owner.last_build_metrics.update(
        {
            "build_mode": "incremental" if compatible else "full",
            "reused_documents": len(reused),
            "artifact_cache_hits": ingestion.cache_hits if ingestion else 0,
            "parsed_documents": ingestion.cache_misses if ingestion else 0,
            "embedding_cache_hits": cached.hits if cached else 0,
            "encoded_texts": cached.encoded if cached else len(new_records),
            "added_chunks": len(new_records),
            "retained_chunks": len(retained),
            "removed_chunks": len(previous.store.records) - len(retained)
            if compatible
            else 0,
        }
    )
    # Managed views are opt-in and version-bound. A default rebuild never runs a sufficiency LLM.
    owner.progress("optional_view_generation")
    owner.view_service.apply(snapshot, embed)
    if cached:
        texts = [r["search_text"] for r in store.records]
        if snapshot.view_store:
            texts.extend(r["search_text"] for r in snapshot.view_store.records)
        snapshot.embedding_cache_keys = [cached.key(text) for text in texts]
        owner.last_build_metrics.update(
            embedding_cache_hits=cached.hits, encoded_texts=cached.encoded
        )
    return snapshot, signature
