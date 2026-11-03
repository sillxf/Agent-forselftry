"""Persisted, incrementally maintained BM25+ term frequencies and postings."""
from collections import Counter
import math
import re

import numpy as np


def tokenize(text: str) -> list[str]:
    terms = re.findall(r"[a-z0-9]+(?:[._:/-][a-z0-9]+)*|[\u3400-\u9fff]", text.lower())
    for run in re.findall(r"[\u3400-\u9fff]{2,}", text):
        terms.extend(run[i:i + 2] for i in range(len(run) - 1))
    return terms


class BM25Statistics:
    """BM25Plus's existing formula; global IDF is derived at scoring, not rebuilt."""
    def __init__(self, owner):
        self.owner = owner

    def get_scores(self, query):
        return np.asarray(self.get_batch_scores(query, list(range(len(self.owner.records)))))

    def get_batch_scores(self, query, doc_ids):
        owner = self.owner
        count = len(owner.records)
        average = owner.total_tokens / count if count else 1
        scores = np.zeros(len(doc_ids))
        for term in query:
            frequency = len(owner.postings.get(term, ()))
            if not frequency:
                continue
            idf = math.log((count + 1) / frequency)
            for position, index in enumerate(doc_ids):
                key = owner.records[index]["chunk_id"]
                terms = owner.terms[key]
                tf = terms.get(term, 0)
                denominator = 1.5 * (0.25 + 0.75 * owner.lengths[key] / average) + tf
                scores[position] += idf * (1 + tf * 2.5 / denominator)
        return scores.tolist()


class SparseRetriever:
    REVISION = 1

    def __init__(self, records, tokenizer=tokenize, *, payload=None):
        self.records = records
        self.tokenizer = tokenizer
        self.terms, self.lengths, self.postings = {}, {}, {}
        self.total_tokens = 0
        if payload is not None:
            if payload["revision"] != self.REVISION:
                raise ValueError("Unsupported sparse index revision")
            self.terms = payload["terms"]
            if set(self.terms) != {r["chunk_id"] for r in records}:
                raise ValueError("Sparse index identities differ from source chunks")
            for key, counts in self.terms.items():
                if not counts or any(not isinstance(n, int) or n <= 0 for n in counts.values()):
                    raise ValueError("Invalid sparse term counts")
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
        removed = {key for key in old if key not in incoming or old[key]["search_text"] != incoming[key]["search_text"]}
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

    def retrieve(self, query: str, limit: int) -> list[dict]:
        tokens = self.tokenizer(query)
        keys = {key for term in set(tokens) for key in self.postings.get(term, ())}
        matches = [i for i, record in enumerate(self.records) if record["chunk_id"] in keys]
        if not matches:
            return []
        scores = self.bm25.get_batch_scores(tokens, matches)
        ranked = sorted(zip(matches, scores), key=lambda item: -item[1])
        return [{**self.records[index], "sparse_score": float(score)} for index, score in ranked[:limit]]
