from functools import lru_cache


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(
        "all-MiniLM-L6-v2"
    )


def embed_texts(texts):
    model = _get_model()

    return model.encode(texts)