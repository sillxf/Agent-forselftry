from functools import lru_cache

from app.config import RAG_EMBEDDING_MODEL


@lru_cache(maxsize=4)
def get_model(model_name: str = RAG_EMBEDDING_MODEL):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)



def get_tokenizer(model_name: str = RAG_EMBEDDING_MODEL):
    return get_model(model_name).tokenizer


def embed_texts(texts, model_name: str = RAG_EMBEDDING_MODEL):
    return get_model(model_name).encode(
        texts, normalize_embeddings=True, convert_to_numpy=True,
    )
