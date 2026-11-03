"""Content-addressed optional embedding reuse; queries do not use this disk cache."""

import hashlib
import json
from pathlib import Path
from uuid import uuid4
from zipfile import BadZipFile

import numpy as np


class CachedEmbedder:
    def __init__(self, embed, root, signature):
        self.embed, self.root, self.signature = embed, Path(root), signature
        self.hits = self.encoded = 0

    def key(self, text):
        payload = json.dumps(
            [self.signature, text],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def __call__(self, texts):
        vectors, missing = {}, {}
        keys = [self.key(text) for text in texts]
        for key, text in zip(keys, texts, strict=True):
            if key in vectors or key in missing:
                continue
            try:
                with np.load(self.root / (key + ".npz"), allow_pickle=False) as cached:
                    vector = cached["vector"]
                    digest = str(cached["sha256"].item())
                if hashlib.sha256(vector.tobytes()).hexdigest() != digest:
                    raise ValueError("Cached embedding checksum mismatch")
                if vector.ndim != 1 or not vector.size or not np.isfinite(vector).all():
                    raise ValueError("Invalid cached vector")
                vectors[key] = vector.astype("float32")
                self.hits += 1
            except (OSError, ValueError, KeyError, EOFError, BadZipFile):
                missing[key] = text
        if missing:
            matrix = np.asarray(self.embed(list(missing.values())), dtype="float32")
            if (
                matrix.ndim != 2
                or matrix.shape[0] != len(missing)
                or not np.isfinite(matrix).all()
            ):
                raise ValueError("Embedding output does not match the requested batch")
            if not matrix.shape[1] or any(
                vector.shape[0] != matrix.shape[1] for vector in vectors.values()
            ):
                raise ValueError(
                    "Cached and fresh embedding dimensions differ; change the cache revision"
                )
            self.root.mkdir(parents=True, exist_ok=True)
            for (key, _), vector in zip(missing.items(), matrix, strict=True):
                temporary = self.root / f".{uuid4().hex}.tmp"
                try:
                    with temporary.open("wb") as stream:
                        np.savez(
                            stream,
                            vector=vector,
                            sha256=hashlib.sha256(vector.tobytes()).hexdigest(),
                        )
                    temporary.replace(self.root / (key + ".npz"))
                finally:
                    temporary.unlink(missing_ok=True)
                vectors[key] = vector
            self.encoded += len(missing)
        if len({vector.shape for vector in vectors.values()}) > 1:
            raise ValueError(
                "Cached and fresh embedding dimensions differ; change the cache revision"
            )
        return np.asarray([vectors[key] for key in keys], dtype="float32")
