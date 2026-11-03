"""Bind immutable snapshots to model adapters and authoritative visibility."""

from app.retrieval.pipeline import RetrievalPipeline


def bind_visibility(pipeline, documents, registry):
    if any(document.version_id for document in documents):
        registry.eligible_ids(
            document.document_id for document in documents if document.version_id
        )

    def eligible():
        mapping = {}
        for document in documents:
            if document.version_id:
                mapping[document.document_id] = document.document_id
            elif not registry.path.exists():
                mapping[document.document_id] = None
            else:
                registered = registry.lookup_path(document.source_path)
                if registered is None:
                    raise ValueError(
                        "Legacy source cannot be resolved in the managed registry; rebuild before serving"
                    )
                mapping[document.document_id] = registered.document_id
        allowed = registry.eligible_ids(
            value for value in mapping.values() if value is not None
        )
        return {
            key for key, value in mapping.items() if value is None or value in allowed
        }

    pipeline.eligibility = eligible


class PipelineFactory:
    def __init__(self, embedding):
        self.embedding = embedding

    def create(self, snapshot, model_name, registry):
        if snapshot.view_store is not None and snapshot.view_model_name != model_name:
            raise ValueError(
                "View index and original index must use the same embedding model"
            )
        pipeline = RetrievalPipeline.from_index(
            snapshot.store,
            {p.parent_id: p for p in snapshot.parents},
            embed=self.embedding(model_name).embed_query,
            view_store=snapshot.view_store,
            sparse=snapshot.sparse,
        )
        bind_visibility(pipeline, snapshot.documents, registry)
        return pipeline
