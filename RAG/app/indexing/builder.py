"""Build-only state: assemble, validate and publish under the single-writer lock."""

from contextlib import nullcontext
from importlib.metadata import version as package_version
from pathlib import Path
import logging, json, sqlite3
from filelock import FileLock, Timeout
from app.ingestion.docling_parser import file_checksum
from app.ingestion.loader import discover_documents
from app.storage.vector_store import FaissVectorStore
from app.storage.snapshot_repository import SavedGeneration
from app.indexing.pipeline import IndexingPipeline
from app.indexing.views import ViewGenerationService

logger = logging.getLogger(__name__)


class IndexBuilder:
    INDEX_VERSION = 8

    def __init__(
        self,
        workspace,
        configuration,
        parser,
        embedding,
        pipeline_factory,
        *,
        progress=None,
        publication_guard=None,
    ):
        self.knowledge_dir, self.storage_dir = (
            workspace.knowledge_dir,
            workspace.storage_dir,
        )
        self.registry, self.lifecycle, self.repository = (
            workspace.registry,
            workspace.lifecycle,
            workspace.repository,
        )
        self.parser, self.embedding_resolver, self.pipeline_factory = (
            parser,
            embedding,
            pipeline_factory,
        )
        self._configured_model_name = "provider:" + configuration.embedding_id
        self.parent_max_tokens, self.child_max_tokens, self.overlap_tokens = (
            configuration.parent_tokens,
            configuration.child_tokens,
            configuration.overlap_tokens,
        )
        self.tokenizer, self.store_factory = None, FaissVectorStore
        self.cache_enabled, self.embedding_cache_revision = True, "1"
        self.last_build_metrics, self.last_build_error = {}, None
        self.progress, self.publication_guard = (
            progress or (lambda stage: None),
            publication_guard or nullcontext,
        )
        self.lock = FileLock(str(self.storage_dir / "build.lock"), timeout=0)
        self.view_service = ViewGenerationService(
            self.registry,
            self.storage_dir,
            self.store_factory,
            self._configured_model_name,
            self.last_build_metrics,
        )

    def _embed(self):
        return self.embedding_resolver(self._configured_model_name).embed_documents

    def _signature(self):
        files = [
            p
            for p in discover_documents(self.knowledge_dir)
            if not self.registry.is_blocked(p)
        ]
        known = {str(p.resolve()) for p in files}
        for document in self.registry.list_documents():
            path = Path(document.source_path)
            if (
                not document.deleted_at
                and not document.purged_at
                and (
                    document.selected_version_id
                    or not path.resolve().is_relative_to(self.knowledge_dir.resolve())
                )
            ):
                if not path.is_file() and not document.selected_version_id:
                    raise ValueError(
                        "An explicitly registered external source is missing"
                    )
                if str(path.resolve()) not in known:
                    files.append(path)
                    known.add(str(path.resolve()))
        files.sort(key=lambda p: str(p.resolve()).lower())

        def checksum(path):
            if path.is_file():
                return file_checksum(path)
            document = self.registry.lookup_path(path)
            versions = self.registry.list_versions(document.document_id)
            return next(
                v.content_hash
                for v in versions
                if v.version_id == document.selected_version_id
            )

        return {
            "version": self.INDEX_VERSION,
            "model": self._configured_model_name,
            "lifecycle_revision": self.registry.revision,
            "embedding_cache_revision": self.embedding_cache_revision,
            "parent_tokens": self.parent_max_tokens,
            "child_tokens": self.child_max_tokens,
            "overlap": self.overlap_tokens,
            "ocr": self.parser.ocr_enabled,
            "processing": {
                "revision": 2,
                "parser": f"{type(self.parser).__module__}.{type(self.parser).__qualname__}",
                "docling": package_version("docling"),
                "transformers": package_version("transformers"),
                "tokenizer": (
                    f"{type(self.tokenizer).__module__}.{type(self.tokenizer).__qualname__}"
                    if self.tokenizer is not None
                    else "embedding-model-tokenizer"
                ),
                "tokenizer_name": str(getattr(self.tokenizer, "name_or_path", "")),
            },
            "files": [
                {"path": str(path.resolve()), "checksum": checksum(path)}
                for path in files
            ],
        }, files

    def _generation(self):
        try:
            pointer = self.repository.current_pointer()
            return pointer["generation"] if pointer else None
        except (OSError, ValueError):
            return None  # Explicit rebuild can repair a damaged current pointer.

    def _previous_generation(self):
        path = self.repository.root / "previous.json"
        try:
            return json.loads(path.read_text(encoding="utf-8"))["generation"]
        except (OSError, ValueError, KeyError):
            return None

    def recover(self):
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        try:
            with self.lock:
                if self.registry.path.exists():
                    self.registry.recover_jobs(
                        self._generation(), self._previous_generation()
                    )
                return True
        except Timeout:
            return (
                False  # A live builder owns the job; it must not be marked interrupted.
            )

    def run(self, *, views=None, full=False):
        owner = self
        if (owner.storage_dir / "service-cutover.json").exists():
            raise ValueError("Legacy writer is retired after service cutover")
        owner.storage_dir.mkdir(parents=True, exist_ok=True)
        with self.lock:
            expected = self._generation()
            owner.registry.recover_jobs(expected, self._previous_generation())
            job = owner.registry.start_job(
                "views" if views is not None else "index", expected
            )
            owner.last_build_metrics.clear()
            try:
                owner.progress("freezing_inputs")
                signature, files = owner._signature()
                if views is None:
                    from app.indexing.incremental import assemble

                    snapshot, signature = assemble(owner, signature, files, full=full)
                else:
                    snapshot = owner.repository.load_current(signature)
                    if snapshot is None:
                        raise ValueError(
                            "Build the original index for the current documents/model before adding views"
                        )
                    snapshot = IndexingPipeline(
                        owner._embed(), owner.store_factory
                    ).build_views(snapshot, views, model_name=signature["model"])
                owner.progress("ready_to_publish")
                owner._publish_snapshot(
                    snapshot, signature, job_id=job, expected_generation=expected
                )
            except Exception as exc:
                owner.last_build_error = str(exc)
                owner.registry.finish_job(
                    job, error=exc, metrics=owner.last_build_metrics
                )
                raise
            try:
                owner.registry.finish_job(job, metrics=owner.last_build_metrics)
            except sqlite3.Error:
                logger.exception(
                    "Generation published; job completion will be reconciled on the next build"
                )
            owner.last_build_error = None
            return job

    def _publish_snapshot(self, snapshot, signature, *, job_id, expected_generation):
        saved = self.repository.save(snapshot, signature)
        self.progress("ready_to_publish")
        with self.publication_guard():
            self.registry.update_job_output(
                job_id, signature["lifecycle_revision"], saved.generation
            )
            self.pipeline_factory.create(snapshot, signature["model"], self.registry)
            with self.registry.publication_guard(signature["lifecycle_revision"]):
                if self._generation() != expected_generation:
                    raise RuntimeError("Stale build: current generation changed")
                self.repository.publish(saved)

    def rollback(self, generation):
        with self.lock:
            expected = self._generation()
            self.registry.recover_jobs(expected, self._previous_generation())
            snapshot = self.repository.load_generation(generation)
            manifest = self.repository._read_manifest(generation)
            if manifest is None or any(not d.version_id for d in snapshot.documents):
                raise ValueError(
                    "Live rollback requires a managed generation with a manifest"
                )
            self.registry.eligible_ids(d.document_id for d in snapshot.documents)
            if self.registry.purged_ids() & {d.document_id for d in snapshot.documents}:
                raise ValueError("Cannot roll back to purged document content")
            signature = manifest["signature"]
            self.pipeline_factory.create(snapshot, signature["model"], self.registry)
            job, revision = (
                self.registry.start_job("rollback", expected),
                self.registry.revision,
            )
            self.registry.update_job_output(job, revision, generation)
            try:
                self.progress("ready_to_publish")
                with (
                    self.publication_guard(),
                    self.registry.publication_guard(revision),
                ):
                    if self._generation() != expected:
                        raise RuntimeError("Stale rollback: current generation changed")
                    self.repository.publish(
                        SavedGeneration(generation, signature), rollback=True
                    )
            except Exception as error:
                self.registry.finish_job(job, error=error)
                raise
            self.registry.finish_job(job)
            return job
