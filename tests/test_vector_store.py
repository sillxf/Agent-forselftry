"""Filtered vector search must equal brute force over the eligible subset."""

import unittest

import numpy as np

from app.storage.vector_store import FaissVectorStore


class FilteredSearchTests(unittest.TestCase):
    def test_selector_matches_brute_force_on_eligible_rows(self):
        rng = np.random.default_rng(0)
        vectors = rng.normal(size=(300, 16)).astype("float32")
        records = [{"chunk_id": str(i), "document_id": str(i % 7)} for i in range(300)]
        store = FaissVectorStore(16)
        store.add(vectors, records)
        allowed = {"1", "3", "4"}
        query = rng.normal(size=16).astype("float32")

        result = store.search_filtered(query, 10, lambda r: r["document_id"] in allowed)

        normalized = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
        scores = normalized @ (query / np.linalg.norm(query))
        eligible = [i for i, r in enumerate(records) if r["document_id"] in allowed]
        expected = sorted(eligible, key=lambda i: -scores[i])[:10]
        self.assertEqual([r["chunk_id"] for r in result], [str(i) for i in expected])
        self.assertTrue(all(r["document_id"] in allowed for r in result))
        np.testing.assert_allclose(
            [r["dense_score"] for r in result], scores[expected], rtol=1e-5
        )

    def test_fewer_eligible_rows_than_k(self):
        store = FaissVectorStore(4)
        store.add(
            np.eye(4, dtype="float32"),
            [{"chunk_id": str(i), "document_id": str(i)} for i in range(4)],
        )
        result = store.search_filtered(
            np.ones(4, dtype="float32"), 10, lambda r: r["document_id"] in {"2"}
        )
        self.assertEqual([r["chunk_id"] for r in result], ["2"])
        self.assertEqual(
            store.search_filtered(np.ones(4, dtype="float32"), 10, lambda r: False), []
        )

    def test_updated_store_keeps_filtered_positions_aligned(self):
        store = FaissVectorStore(4)
        store.add(
            np.eye(4, dtype="float32"),
            [{"chunk_id": str(i), "document_id": str(i)} for i in range(4)],
        )
        updated = store.updated({"0"}, [], [])
        query = np.array([0, 0, 1, 0], dtype="float32")
        result = updated.search_filtered(query, 1, lambda r: r["document_id"] != "3")
        self.assertEqual(result[0]["chunk_id"], "2")


if __name__ == "__main__":
    unittest.main()
