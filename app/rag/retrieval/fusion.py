"""Equal-weight reciprocal-rank fusion for any number of retrieval routes."""


class RRFFusion:
    def __init__(self, rank_constant=60):
        self.rank_constant = rank_constant

    def fuse(self, rankings: list[list[dict]]) -> list[dict]:
        scores, records = {}, {}
        for ranking in rankings:
            seen = set()
            for rank, record in enumerate(ranking, 1):
                key = record["chunk_id"]
                if key in seen:
                    continue
                seen.add(key)
                scores[key] = scores.get(key, 0.0) + 1.0 / (self.rank_constant + rank)
                records[key] = {**records.get(key, {}), **record}
        keys = sorted(scores, key=lambda key: (
            -scores[key], -records[key].get("sparse_score", 0.0),
            -records[key].get("dense_score", -1.0),
            records[key].get("retrieval_key") or key, records[key].get("source_name", ""), key,
        ))
        return [{**records[key], "score": scores[key]} for key in keys]
