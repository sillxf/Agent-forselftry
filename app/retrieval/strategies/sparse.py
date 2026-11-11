"""Persisted, incrementally maintained BM25+ term frequencies and postings."""

from collections import Counter
import math
import re
from threading import Lock

import numpy as np

from app.core.exceptions import IndexIntegrityError


def tokenize(text: str) -> list[str]:
    terms = re.findall(r"[a-z0-9]+(?:[._:/-][a-z0-9]+)*|[\u3400-\u9fff]", text.lower())
    for run in re.findall(r"[\u3400-\u9fff]{2,}", text):
        terms.extend(run[i : i + 2] for i in range(len(run) - 1))
    return terms


class BM25Statistics:
    """BM25Plus's existing formula; global IDF is derived at scoring, not rebuilt.

    Scoring runs as numpy operations over the matched rows instead of a Python
    loop per row and term. Each row receives the same float operations in the
    same order as before, so scores and ties are bit-identical. Per-term posting
    arrays are built on first use and kept: the snapshot is immutable.
    """

    def __init__(self, owner):
        self.owner = owner
        self._rows = self._base = self._documents = self._codes = None
        self._postings = {}
        self._lock = Lock()

    def _prepare(self):
        with self._lock:
            if self._rows is not None:
                return
            owner = self.owner
            count = len(owner.records)
            average = owner.total_tokens / count if count else 1
            keys = [r["chunk_id"] for r in owner.records]
            lengths = np.asarray([owner.lengths[k] for k in keys], dtype="float64")
            codes, documents = [], {}
            for record in owner.records:
                codes.append(documents.setdefault(record["document_id"], len(documents)))
            self._base = 1.5 * (0.25 + 0.75 * lengths / average)
            self._codes = np.asarray(codes, dtype="int64")
            self._documents = documents
            self._rows = {key: i for i, key in enumerate(keys)}

    def _posting(self, term):
        cached = self._postings.get(term)
        if cached is None:
            owner, keys = self.owner, self.owner.postings.get(term, ())
            rows = np.fromiter((self._rows[k] for k in keys), "int64", len(keys))
            tf = np.fromiter((owner.terms[k][term] for k in keys), "float64", len(keys))
            order = np.argsort(rows)
            cached = self._postings[term] = (rows[order], tf[order])
        return cached

    def get_scores(self, query):
        return self.get_batch_scores(query, np.arange(len(self.owner.records)))

    def get_batch_scores(self, query, doc_ids):
        """Scores for row indices doc_ids (sorted ascending), in that order."""
        self._prepare()
        rows = np.asarray(doc_ids, dtype="int64")
        count = len(self.owner.records)
        base = self._base[rows]
        scores = np.zeros(len(rows))
        for term in query:  # Repeated query terms count again, as before.
            posting_rows, posting_tf = self._posting(term)
            if not len(posting_rows):
                continue
            idf = math.log((count + 1) / len(posting_rows))
            tf = np.zeros(len(rows))
            where = np.searchsorted(rows, posting_rows)
            inside = where < len(rows)
            inside[inside] = rows[where[inside]] == posting_rows[inside]
            tf[where[inside]] = posting_tf[inside]
            scores += idf * (1 + tf * 2.5 / (base + tf))
        return scores

    def matches(self, tokens, allowed_ids=None):
        """Rows containing any query term, ascending, optionally limited to documents."""
        self._prepare()
        hit = np.zeros(len(self.owner.records), dtype=bool)
        for term in set(tokens):
            hit[self._posting(term)[0]] = True
        if allowed_ids is not None:
            permitted = np.zeros(len(self._documents) + 1, dtype=bool)
            for identity in allowed_ids:
                code = self._documents.get(identity)
                if code is not None:
                    permitted[code] = True
            hit &= permitted[self._codes]
        return np.flatnonzero(hit)


class SparseRetriever:
    REVISION = 1

    def __init__(self, records, tokenizer=tokenize, *, payload=None):
        self.records = records
        self.tokenizer = tokenizer
        self.terms, self.lengths, self.postings = {}, {}, {}
        self.total_tokens = 0
        if payload is not None:
            if payload["revision"] != self.REVISION:
                raise IndexIntegrityError("Unsupported sparse index revision")
            self.terms = payload["terms"]
            if set(self.terms) != {r["chunk_id"] for r in records}:
                raise IndexIntegrityError("Sparse index identities differ from source chunks")
            for key, counts in self.terms.items():
                if not counts or any(
                    not isinstance(n, int) or n <= 0 for n in counts.values()
                ):
                    raise IndexIntegrityError("Invalid sparse term counts")
                self._add_statistics(key, counts)
        else:
            for record in records:
                self._add(record)
        self.bm25 = BM25Statistics(self) if records else None

    def _add_statistics(self, key, counts):
        length = sum(counts.values())
        self.lengths[key] = length
        self.total_tokens += length
        for term in counts:
            self.postings.setdefault(term, set()).add(key)

    def _add(self, record):
        counts = dict(Counter(self.tokenizer(record["search_text"]) or ["__empty__"]))
        self.terms[record["chunk_id"]] = counts
        self._add_statistics(record["chunk_id"], counts)

    def updated(self, records):
        """Copy-on-write postings; tokenize only added/replaced chunk identities."""
        result = object.__new__(type(self))
        result.records, result.tokenizer = records, self.tokenizer
        result.terms = dict(self.terms)
        result.lengths = dict(self.lengths)
        result.postings = {term: set(keys) for term, keys in self.postings.items()}
        result.total_tokens = self.total_tokens
        incoming = {r["chunk_id"]: r for r in records}
        old = {r["chunk_id"]: r for r in self.records}
        removed = {
            key
            for key in old
            if key not in incoming
            or old[key]["search_text"] != incoming[key]["search_text"]
        }
        for key in removed:
            counts = result.terms.pop(key)
            result.total_tokens -= result.lengths.pop(key)
            for term in counts:
                result.postings[term].remove(key)
                if not result.postings[term]:
                    del result.postings[term]
        for record in records:
            if record["chunk_id"] not in result.terms:
                result._add(record)
        result.bm25 = BM25Statistics(result) if records else None
        return result

    def payload(self):
        return {"revision": self.REVISION, "terms": self.terms}

    supports_filter = True

    def retrieve(self, query: str, limit: int, *, allowed_ids=None) -> list[dict]:
        tokens = self.tokenizer(query)
        if self.bm25 is None or not tokens or limit <= 0:
            return []
        matches = self.bm25.matches(tokens, allowed_ids)
        if not len(matches):
            return []
        scores = self.bm25.get_batch_scores(tokens, matches)
        # Stable sort on the negated score: ties keep record order, as before.
        order = np.argsort(-scores, kind="stable")[:limit]
        return [
            {**self.records[int(matches[i])], "sparse_score": float(scores[i])}
            for i in order
        ]
