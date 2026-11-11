"""BM25Plus retrieval with security-aware tokenization and candidate-only scoring."""
import re

from rank_bm25 import BM25Plus


def tokenize(text: str) -> list[str]:
    """Keep security identifiers intact; Chinese does not depend on whitespace."""
    terms = re.findall(r"[a-z0-9]+(?:[._:/-][a-z0-9]+)*|[\u3400-\u9fff]", text.lower())
    for run in re.findall(r"[\u3400-\u9fff]{2,}", text):
        terms.extend(run[i:i + 2] for i in range(len(run) - 1))
    return terms


class SparseRetriever:
    def __init__(self, records, tokenizer=tokenize):
        self.records = records
        self.tokenizer = tokenizer
        tokens = [tokenizer(record["search_text"]) for record in records]
        # BM25+ avoids zero/negative IDF for identifiers in tiny knowledge bases.
        self.bm25 = BM25Plus([terms or ["__empty__"] for terms in tokens]) if tokens else None
        self.postings = {}
        for index, terms in enumerate(tokens):
            for term in set(terms):
                self.postings.setdefault(term, []).append(index)

    def retrieve(self, query: str, limit: int) -> list[dict]:
        tokens = self.tokenizer(query)
        # Corpus order breaks ties; repeated query terms still contribute to scores.
        matches = sorted({index for term in set(tokens) for index in self.postings.get(term, ())})
        if not matches:
            return []
        scores = self.bm25.get_batch_scores(tokens, matches)
        ranked = sorted(zip(matches, scores), key=lambda item: -item[1])
        return [{**self.records[index], "sparse_score": float(score)}
                for index, score in ranked[:limit]]
