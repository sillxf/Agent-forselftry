"""Select published/current candidates and filter metadata before Top-K.

Filter syntax (a JSON object; all top-level entries must hold):
  {"file_type": "pdf"}                       equals
  {"metadata.team": ["red", "blue"]}         any of
  {"metadata.year": {"$gte": "2024"}}        operator object
  {"$or": [{"source": "a.pdf"}, {"metadata.team": "red"}]}
Fields: document_id, file_type, source (file name) and metadata.<key>.
Operators: $eq $ne $in $nin $gt $gte $lt $lte $contains $exists.
Ordering compares numbers when both sides are numeric, otherwise text, so ISO
dates such as "2024-05-01" order correctly. Missing fields never match, except
for $ne, $nin and {"$exists": false}.
"""

from copy import copy
from pathlib import Path
import re

from app.core.exceptions import InvalidRequest
from app.retrieval.history import HistoricalQuery

FIELD = re.compile(r"document_id|file_type|source|metadata\.[\w.-]{1,80}")
OPERATORS = {"$eq", "$ne", "$in", "$nin", "$gt", "$gte", "$lt", "$lte", "$contains", "$exists"}
MAX_CONDITIONS, MAX_DEPTH, MAX_VALUES, MAX_TEXT = 20, 3, 50, 1000


def _scalar(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise InvalidRequest("Filter values must be text or numbers")
    value = str(value)
    if len(value) > MAX_TEXT:
        raise InvalidRequest("Metadata filter is too large")
    return value


def compile_filters(filters, depth=0, budget=None):
    """Validate once and return a predicate over a field-lookup function."""
    budget = budget if budget is not None else [0]
    if not isinstance(filters, dict):
        raise InvalidRequest("Filters must be an object")
    if depth > MAX_DEPTH:
        raise InvalidRequest("Filters are nested too deeply")
    checks = []
    for key, expected in filters.items():
        if key in {"$and", "$or"}:
            if not isinstance(expected, list) or not expected:
                raise InvalidRequest(f"{key} needs a non-empty list of filters")
            parts = [compile_filters(f, depth + 1, budget) for f in expected]
            combine = all if key == "$and" else any
            checks.append(lambda get, p=parts, c=combine: c(x(get) for x in p))
            continue
        if not FIELD.fullmatch(key):
            raise InvalidRequest("Unsupported metadata filter")
        budget[0] += 1
        if budget[0] > MAX_CONDITIONS:
            raise InvalidRequest(f"At most {MAX_CONDITIONS} filter conditions")
        if isinstance(expected, dict):
            if not expected or set(expected) - OPERATORS:
                raise InvalidRequest(
                    "Unknown filter operator; use " + " ".join(sorted(OPERATORS))
                )
            for operator, value in expected.items():
                checks.append(_condition(key, operator, value))
        elif isinstance(expected, list):
            checks.append(_condition(key, "$in", expected))
        else:
            checks.append(_condition(key, "$eq", expected))
    return lambda get: all(check(get) for check in checks)


def _number(text):
    try:
        return float(text)
    except ValueError:
        return None


def _order(actual, expected):
    a, b = _number(actual), _number(expected)
    return (a, b) if a is not None and b is not None else (actual, expected)


def _condition(field, operator, value):
    if operator == "$exists":
        if not isinstance(value, bool):
            raise InvalidRequest("$exists takes true or false")
        return lambda get: (get(field) is not None) == value
    if operator in {"$in", "$nin"}:
        if not isinstance(value, list) or len(value) > MAX_VALUES:
            raise InvalidRequest(f"{operator} takes a list of at most {MAX_VALUES} values")
        options = {_scalar(v) for v in value}
        if operator == "$in":
            return lambda get: get(field) in options
        return lambda get: get(field) not in options
    expected = _scalar(value)
    if operator == "$eq":
        return lambda get: get(field) == expected
    if operator == "$ne":
        return lambda get: get(field) != expected
    if operator == "$contains":
        needle = expected.casefold()
        return lambda get: get(field) is not None and needle in get(field).casefold()
    compare = {
        "$gt": lambda a, b: a > b,
        "$gte": lambda a, b: a >= b,
        "$lt": lambda a, b: a < b,
        "$lte": lambda a, b: a <= b,
    }[operator]
    return lambda get: get(field) is not None and compare(*_order(get(field), expected))


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
    predicate = compile_filters(filters) if filters else None

    def eligible():
        ids = (
            original()
            if original
            else {x["document_id"] for x in source.dense.store.records}
        )
        if predicate is None:
            return ids
        docs = {d.document_id: d for d in runtime.workspace.registry.list_documents()}
        types = {
            x["document_id"]: x.get("file_type", "") for x in source.dense.store.records
        }

        def match(identity):
            document = docs[identity]

            def get(field):
                if field == "document_id":
                    return identity
                if field == "file_type":
                    return types.get(identity)
                if field == "source":
                    return Path(document.source_path).name
                return document.metadata.get(field.removeprefix("metadata."))

            return predicate(get)

        return {i for i in ids if i in docs and match(i)}

    pipeline.eligibility = eligible
    return pipeline
