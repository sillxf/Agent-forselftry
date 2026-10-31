import numpy as np

from app.rag.indexing.vector_store import FaissVectorStore


def test_cosine_ranking_and_disk_round_trip(tmp_path):
    store = FaissVectorStore(2)
    vectors = np.array([[5., 0.], [0., 4.]], dtype="float32")
    store.add(vectors, [{"chunk_id": "a"}, {"chunk_id": "b"}])
    results = store.search([1, 0], 20)
    assert len(results) == 2 and results[0]["chunk_id"] == "a"
    store.save(tmp_path / "中文索引")
    restored = FaissVectorStore.load(tmp_path / "中文索引")
    assert restored.search([1, 0], 20) == results
