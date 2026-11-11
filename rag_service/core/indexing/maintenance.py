"""Explicit retention under the same build lock; no source-version purge."""

import json
import re
import shutil
import time
from filelock import FileLock, Timeout


def collect_generations(build_service, *, keep=3, min_age_seconds=86400):
    if keep < 2 or min_age_seconds < 0:
        raise ValueError(
            "Retain at least two generations and use a nonnegative grace period"
        )
    owner = build_service.owner
    root = owner.repository.root
    if not root.exists():
        return {"generations": [], "artifacts": [], "embeddings": []}
    removed, artifacts, embeddings = [], [], []
    with build_service.lock:
        protected = set()
        for name in ("current.json", "previous.json"):
            path = root / name
            if path.exists():
                protected.add(
                    json.loads(path.read_text(encoding="utf-8"))["generation"]
                )
        for name in protected:
            if not (root / name).is_dir():
                raise ValueError(
                    "A protected generation is missing; repair before collecting"
                )
            owner.repository._read_manifest(name)
        candidates = [
            path
            for path in root.iterdir()
            if path.is_dir()
            and not path.is_symlink()
            and re.fullmatch(r"[0-9a-f]{32}", path.name)
        ]
        candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
        retained = set(protected)
        for path in candidates:
            if len(retained) >= keep:
                break
            retained.add(path.name)
        now = time.time()
        for path in candidates:
            # Both the identifier and resolved parent are checked before recursive removal.
            if path.name in retained or now - path.stat().st_mtime < min_age_seconds:
                continue
            if path.resolve().parent != root.resolve():
                raise ValueError(
                    "Refusing to collect a generation outside the index root"
                )
            try:
                with FileLock(str(root / f".read-{path.name}.lock"), timeout=0):
                    shutil.rmtree(path)
                    removed.append(path.name)
            except Timeout:
                continue  # A reader is loading this snapshot; retain it and its cache references.
        referenced, embedding_keys = set(), set()
        for path in candidates:
            if not path.exists():
                continue
            manifest = path / "manifest.json"
            if manifest.exists():
                value = json.loads(manifest.read_text(encoding="utf-8"))
                referenced.update(
                    item["artifact_id"]
                    for item in value["documents"]
                    if item.get("artifact_id")
                )
                embedding_keys.update(value.get("embedding_cache_keys", []))
        cache = owner.storage_dir / "artifacts"
        if cache.exists():
            for path in cache.glob("*.json"):
                if (
                    re.fullmatch(r"[0-9a-f]{64}", path.stem)
                    and path.stem not in referenced
                    and now - path.stat().st_mtime >= min_age_seconds
                ):
                    if path.is_symlink() or path.resolve().parent != cache.resolve():
                        raise ValueError(
                            "Refusing to collect an artifact outside the cache root"
                        )
                    path.unlink()
                    artifacts.append(path.stem)
        cache = owner.storage_dir / "embedding_cache"
        if cache.exists():
            for path in cache.glob("*.npz"):
                if (
                    re.fullmatch(r"[0-9a-f]{64}", path.stem)
                    and path.stem not in embedding_keys
                    and now - path.stat().st_mtime >= min_age_seconds
                ):
                    if path.is_symlink() or path.resolve().parent != cache.resolve():
                        raise ValueError(
                            "Refusing to collect an embedding outside the cache root"
                        )
                    path.unlink()
                    embeddings.append(path.stem)
    return {"generations": removed, "artifacts": artifacts, "embeddings": embeddings}
