"""Single-writer build orchestration; expensive work never holds the query lock."""
import logging
import json
import sqlite3

from filelock import FileLock, Timeout

from app.rag.indexing.pipeline import IndexingPipeline
from app.rag.indexing.snapshot_repository import SavedGeneration


logger = logging.getLogger(__name__)


class BuildService:
    def __init__(self, retriever):
        self.owner = retriever
        self.lock = FileLock(str(retriever.storage_dir / "build.lock"), timeout=0)

    def _generation(self):
        try:
            pointer = self.owner.repository.current_pointer()
            return pointer["generation"] if pointer else None
        except (OSError, ValueError):
            return None  # Explicit rebuild can repair a damaged current pointer.

    def _previous_generation(self):
        path = self.owner.repository.root / "previous.json"
        try:
            return json.loads(path.read_text(encoding="utf-8"))["generation"]
        except (OSError, ValueError, KeyError):
            return None

    def recover(self):
        if not self.owner.registry.path.exists():
            return False
        try:
            with self.lock:
                self.owner.registry.recover_jobs(self._generation(), self._previous_generation())
                return True
        except Timeout:
            return False  # A live builder owns the job; it must not be marked interrupted.

    def run(self, *, views=None):
        owner = self.owner
        owner.storage_dir.mkdir(parents=True, exist_ok=True)
        with self.lock:
            expected = self._generation()
            owner.registry.recover_jobs(expected, self._previous_generation())
            job = owner.registry.start_job("views" if views is not None else "index", expected)
            owner.last_build_metrics = {}
            try:
                signature, files = owner._signature()
                if views is None:
                    snapshot, signature = owner._assemble_snapshot(signature, files)
                else:
                    snapshot = owner.repository.load_current(signature)
                    if snapshot is None:
                        raise ValueError("Build the original index for the current documents/model before adding views")
                    snapshot = IndexingPipeline(owner._embed(), owner.store_factory).build_views(
                        snapshot, views, model_name=signature["model"])
                owner._publish_snapshot(snapshot, signature, job_id=job, expected_generation=expected)
            except Exception as exc:
                owner.last_build_error = str(exc)
                owner.registry.finish_job(job, error=exc, metrics=owner.last_build_metrics)
                raise
            try:
                owner.registry.finish_job(job, metrics=owner.last_build_metrics)
            except sqlite3.Error:
                logger.exception("Generation published; job completion will be reconciled on the next build")
            owner.last_build_error = None
            return job

    def rollback(self, generation):
        owner = self.owner
        owner.storage_dir.mkdir(parents=True, exist_ok=True)
        with self.lock:
            expected = self._generation()
            owner.registry.recover_jobs(expected, self._previous_generation())
            snapshot = owner.repository.load_generation(generation)
            manifest = owner.repository._read_manifest(generation)
            if manifest is None or any(not doc.version_id for doc in snapshot.documents):
                raise ValueError("Live rollback requires a managed generation with a manifest")
            owner.registry.eligible_ids(doc.document_id for doc in snapshot.documents)
            signature = manifest["signature"]
            parents = {parent.parent_id: parent for parent in snapshot.parents}
            pipeline = owner._prepare_pipeline(snapshot.store, parents, signature["model"],
                                               **owner._view_options(snapshot))
            owner._bind_live_filter(pipeline, snapshot.documents)
            pipeline.generation_id = generation
            job = owner.registry.start_job("rollback", expected)
            revision = owner.registry.revision
            owner.registry.update_job_output(job, revision, generation)
            try:
                with owner.registry.publication_guard(revision), owner._lock:
                    if self._generation() != expected:
                        raise RuntimeError("Stale rollback: current generation changed")
                    owner._publishing = True
                    try:
                        owner.repository.publish(SavedGeneration(generation, signature), rollback=True)
                        owner._activate_index(snapshot.store, snapshot.documents, parents, pipeline, signature["model"])
                        owner._generation_id, owner._follow_current = generation, True
                    finally:
                        owner._publishing = False
            except Exception as exc:
                owner.registry.finish_job(job, error=exc, metrics=owner.last_build_metrics)
                raise
            owner.registry.finish_job(job)
            return job
