"""Select published/current candidates and filter metadata before Top-K."""

from copy import copy
import re
from app.retrieval.history import HistoricalQuery
from app.core.exceptions import InvalidRequest


def filtered_pipeline(runtime, request):
    if request.as_of:
        snapshot, publication = runtime.workspace.repository.at(request.as_of)
        source = HistoricalQuery(runtime, snapshot, publication, request.as_of).pipeline
    else:
        source = runtime.pipeline
    pipeline = copy(source)
    pipeline.route_trace = []
    original = source.eligibility
    filters = request.filters
    if any(
        not (
            k in {"document_id", "file_type"}
            or re.fullmatch(r"metadata\.[\w-]{1,80}", k)
        )
        for k in filters
    ):
        raise InvalidRequest("Unsupported metadata filter")
    if any(
        len(v if isinstance(v, list) else [v]) > 50
        or any(len(x) > 1000 for x in (v if isinstance(v, list) else [v]))
        for v in filters.values()
    ):
        raise InvalidRequest("Metadata filter is too large")

    def eligible():
        ids = (
            original()
            if original
            else {x["document_id"] for x in source.dense.store.records}
        )
        if not filters:
            return ids
        docs = {d.document_id: d for d in runtime.workspace.registry.list_documents()}
        types = {
            x["document_id"]: x.get("file_type", "") for x in source.dense.store.records
        }

        def match(identity):
            document = docs[identity]
            for field, expected in filters.items():
                actual = (
                    identity
                    if field == "document_id"
                    else types.get(identity)
                    if field == "file_type"
                    else document.metadata.get(field.removeprefix("metadata."))
                )
                if actual not in (
                    expected if isinstance(expected, list) else [expected]
                ):
                    return False
            return True

        return {i for i in ids if i in docs and match(i)}

    pipeline.eligibility = eligible
    return pipeline
