"""Restore ranked Child hits into independently deduplicated Parent contexts."""


class ParentContextBuilder:
    def __init__(self, parents):
        self.parents = parents

    def build(self, ranked_candidates: list[dict], k: int) -> list[dict]:
        if k <= 0:
            return []
        results, seen = [], set()
        for item in ranked_candidates:
            parent = self.parents[item["parent_id"]]
            if parent.parent_id in seen:
                continue
            seen.add(parent.parent_id)
            results.append(
                {
                    **item,
                    "source": item["source_name"],
                    "chunk_content": item["content"],
                    "content": parent.content,
                    "page_start": parent.page_start,
                    "page_end": parent.page_end,
                    "matched_page_start": item["page_start"],
                    "matched_page_end": item["page_end"],
                    "image_paths": list(
                        dict.fromkeys(
                            b.image_path for b in parent.blocks if b.image_path
                        )
                    ),
                }
            )
            if len(results) >= k:
                break
        return results
