"""Evidence coverage plus result-level ranking metrics (contract result-qrels-v2)."""

from math import log2

METRIC_CONTRACT = "result-qrels-v2"


def retrieval_metrics(
    ranked_matches: list[list[str]],
    grades: dict[str, int],
    k: int,
    *,
    ideal_result_grades: list[int],
) -> dict:
    """Each input slot is a distinct child or parent; misses keep their real rank.

    Recall covers unique facts. Precision/MRR/DCG judge each result's maximum fact
    grade, including distinct results supporting the same fact. IDCG must use grades
    derived from ALL indexed units of that same type, never from evidence counts or
    merely the retrieved top K. Ground-truth alternatives do not add required facts.
    """
    if k <= 0:
        raise ValueError("k must be positive")
    relevant = {key: grade for key, grade in grades.items() if grade > 0}
    if not relevant:
        return dict(recall=None, precision=None, mrr=None, ndcg=None)
    seen, first_rank, hit_slots, dcg = set(), None, 0, 0.0
    for rank, matches in enumerate(ranked_matches[:k], 1):
        found = set(matches) & relevant.keys()
        if not found:
            continue
        seen.update(found)
        hit_slots += 1
        first_rank = first_rank or rank
        dcg += (2 ** max(relevant[key] for key in found) - 1) / log2(rank + 1)
    ideal = sum(
        (2**grade - 1) / log2(rank + 1)
        for rank, grade in enumerate(sorted(ideal_result_grades, reverse=True)[:k], 1)
    )
    return dict(
        recall=len(seen) / len(relevant),
        precision=hit_slots / k,
        mrr=1 / first_rank if first_rank else 0.0,
        ndcg=dcg / ideal if ideal else 0.0,
    )
