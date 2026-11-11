"""BM25 scoring must match the plain per-row formula exactly, including ties."""

import math
import random
import unittest

from app.retrieval.strategies.sparse import SparseRetriever, tokenize


def reference(records, query, limit, allowed=None):
    """The pre-1.3 Python implementation, kept here as the specification."""
    terms = {r["chunk_id"]: {} for r in records}
    for r in records:
        for t in tokenize(r["search_text"]) or ["__empty__"]:
            terms[r["chunk_id"]][t] = terms[r["chunk_id"]].get(t, 0) + 1
    lengths = {k: sum(v.values()) for k, v in terms.items()}
    postings = {}
    for k, counts in terms.items():
        for t in counts:
            postings.setdefault(t, set()).add(k)
    tokens = tokenize(query)
    keys = {k for t in set(tokens) for k in postings.get(t, ())}
    rows = [
        i
        for i, r in enumerate(records)
        if r["chunk_id"] in keys and (allowed is None or r["document_id"] in allowed)
    ]
    average = sum(lengths.values()) / len(records)
    scored = []
    for i in rows:
        key, score = records[i]["chunk_id"], 0.0
        for t in tokens:
            if t not in postings:
                continue
            idf = math.log((len(records) + 1) / len(postings[t]))
            tf = terms[key].get(t, 0)
            score += idf * (1 + tf * 2.5 / (1.5 * (0.25 + 0.75 * lengths[key] / average) + tf))
        scored.append((i, score))
    scored.sort(key=lambda item: -item[1])
    return [(records[i]["chunk_id"], s) for i, s in scored[:limit]]


class SparseTests(unittest.TestCase):
    def test_vectorized_scores_equal_reference_formula(self):
        rng = random.Random(3)
        words = "login failed credential lsass t1003 横向 移动 凭据 转储 日志".split()
        records = [
            dict(
                chunk_id=f"c{i}",
                document_id=f"d{i // 4}",
                search_text=" ".join(rng.choice(words) for _ in range(rng.randint(1, 30))),
            )
            for i in range(200)
        ]
        records.append(dict(chunk_id="empty", document_id="dx", search_text="!!"))
        sparse = SparseRetriever(records)
        allowed = {f"d{i}" for i in range(0, 50, 2)}
        for query in ["login lsass", "凭据转储 横向移动", "t1003 t1003", "nothing", "日志"]:
            for subset in (None, allowed):
                got = [
                    (r["chunk_id"], r["sparse_score"])
                    for r in sparse.retrieve(query, 25, allowed_ids=subset)
                ]
                self.assertEqual(got, reference(records, query, 25, subset), query)
        changed = records[:100] + [
            dict(chunk_id="new", document_id="dn", search_text="lsass lsass login")
        ]
        self.assertEqual(
            [(r["chunk_id"], r["sparse_score"]) for r in sparse.updated(changed).retrieve("lsass login", 10)],
            reference(changed, "lsass login", 10),
        )

    def test_empty_index_and_query(self):
        self.assertEqual(SparseRetriever([]).retrieve("anything", 5), [])
        one = SparseRetriever([dict(chunk_id="a", document_id="d", search_text="x y")])
        self.assertEqual(one.retrieve("", 5), [])
        self.assertEqual(one.retrieve("x", 5, allowed_ids=set()), [])


if __name__ == "__main__":
    unittest.main()
