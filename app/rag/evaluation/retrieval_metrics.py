"""Rank-preserving, novelty-aware metrics over evidence matches at each result rank."""
from math import log2


def retrieval_metrics(ranked_matches: list[list[str]], grades: dict[str, int], k: int) -> dict:
    """Empty/duplicate result slots remain in place; one slot can cover multiple evidence IDs.

    Recall counts unique evidence. Precision counts slots introducing positive evidence / K.
    NDCG uses max newly covered grade per slot, exponential gain, and evidence-level IDCG.
    This explicit novelty convention prevents overlap duplicates from inflating quality.
    """
    if k <= 0:
        raise ValueError("k must be positive")
    relevant = {key: grade for key, grade in grades.items() if grade > 0}
    if not relevant:
        return dict(recall=None, precision=None, mrr=None, ndcg=None)
    seen, first_rank, hit_slots, dcg = set(), None, 0, 0.0
    for rank, matches in enumerate(ranked_matches[:k], 1):
        new = (set(matches) & relevant.keys()) - seen
        if not new:
            continue
        seen.update(new)
        hit_slots += 1
        first_rank = first_rank or rank
        dcg += (2 ** max(relevant[key] for key in new) - 1) / log2(rank + 1)
    ideal = sum((2 ** grade - 1) / log2(rank + 1)
                for rank, grade in enumerate(sorted(relevant.values(), reverse=True)[:k], 1))
    return dict(recall=len(seen) / len(relevant), precision=hit_slots / k,
                mrr=1 / first_rank if first_rank else 0.0, ndcg=dcg / ideal)
