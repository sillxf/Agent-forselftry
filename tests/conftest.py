"""Offline RAG fixtures: real parsing/FAISS, deterministic local embeddings."""
import hashlib
import re

import numpy as np
import pytest

from app.rag.retriever import KnowledgeRetriever


class CharacterTokenizer:
    def encode(self, text, add_special_tokens=False):
        return list(text)


class LocalEmbedder:
    def __init__(self):
        self.calls = []

    def __call__(self, texts):
        self.calls.append(list(texts))
        vectors = np.zeros((len(texts), 32), dtype="float32")
        for index, text in enumerate(texts):
            for word in re.findall(r"[a-z0-9]+", text.lower()):
                slot = int(hashlib.sha256(word.encode()).hexdigest()[:8], 16) % 32
                vectors[index, slot] += 1
        return vectors


@pytest.fixture
def rag_factory(tmp_path):
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir()
    storage = tmp_path / "storage"

    def create(build=True, **options):
        defaults = dict(knowledge_dir=knowledge, storage_dir=storage, tokenizer=CharacterTokenizer(),
                        embedding_fn=LocalEmbedder(), model_name="test-local-v1",
                        child_max_tokens=240, overlap_tokens=25)
        defaults.update(options)
        return KnowledgeRetriever(build=build, **defaults)

    create.knowledge = knowledge
    create.storage = storage
    return create
