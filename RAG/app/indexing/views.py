"""Opt-in, version-bound offline question generation. No retrieval-quality experiment."""

import hashlib
import json
import math
import os
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.indexing.pipeline import IndexingPipeline
from app.indexing.view_models import (
    PROMPT_VERSION,
    RetrievalView,
    generate_question_views,
    validate_views,
)


class ViewConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    enabled: bool = False
    model: str | None = Field(default=None, min_length=1, max_length=200)
    prompt_version: Literal["question-view-v1"] = PROMPT_VERSION
    batch_size: int = Field(default=8, ge=1, le=32)
    max_requests: int = Field(default=8, ge=1, le=100)
    timeout_seconds: float = Field(default=90, gt=0, le=180)
    max_completion_tokens: int = Field(default=2048, ge=128, le=8192)
    failure_policy: Literal["publish_without_views", "fail_build"] = (
        "publish_without_views"
    )


def digest(payload):
    return hashlib.sha256(
        json.dumps(
            payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        ).encode()
    ).hexdigest()


class RecordedGenerator:
    def __init__(self, client, usage):
        self.client, self.model, self.usage = client, client.model, usage

    def generate(self, prompt):
        self.usage["requests"] += 1
        response = self.client.chat(messages=[{"role": "user", "content": prompt}])
        reported = response.get("usage")
        if reported:
            self.usage["reported_requests"] += 1
            for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
                self.usage[key] += reported.get(key) or 0
        return response["content"]


class ViewGenerationService:
    def __init__(
        self,
        registry,
        storage_dir,
        store_factory,
        model_name,
        metrics,
        *,
        llm_factory=None,
    ):
        self.registry, self.store_factory, self.model_name, self.metrics = (
            registry,
            store_factory,
            model_name,
            metrics,
        )
        self.llm_factory = llm_factory
        self.root = storage_dir / "views"

    @staticmethod
    def resolved_config(raw):
        config = ViewConfig.model_validate(raw)
        model = (
            config.model or os.getenv("RAG_VIEW_LLM_MODEL") or os.getenv("LLM_MODEL")
        )
        return config.model_copy(update={"model": model})

    def _client(self, config):
        if self.llm_factory:
            return self.llm_factory(config)
        from app.models.llm.client import LLMClient

        return LLMClient(
            os.getenv("RAG_VIEW_LLM_API_KEY") or os.getenv("LLM_API_KEY"),
            os.getenv("RAG_VIEW_LLM_BASE_URL") or os.getenv("LLM_BASE_URL"),
            config.model,
            timeout=config.timeout_seconds,
            max_retries=0,
            max_completion_tokens=config.max_completion_tokens,
        )

    def _cached(self, key, document, config, records):
        try:
            wrapper = json.loads(
                (self.root / (key + ".json")).read_text(encoding="utf-8")
            )
            payload = wrapper["payload"]
            if (
                wrapper["sha256"] != digest(payload)
                or payload["artifact_id"] != document.artifact_id
                or payload["config"] != config.model_dump()
            ):
                return None
            views = [RetrievalView.model_validate(item) for item in payload["views"]]
            validate_views(views, records)
            return views
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def apply(self, snapshot, embed):
        registry = self.registry
        all_views, pending = [], []
        usage = {
            "requests": 0,
            "reported_requests": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }
        for document in snapshot.documents:
            config = self.resolved_config(
                registry.get_document(document.document_id).view_config
            )
            if not config.enabled:
                registry.invalidate_views(document.document_id)
                continue
            records = [
                r
                for r in snapshot.store.records
                if r["document_id"] == document.document_id
            ]
            key = digest(
                [
                    document.document_id,
                    document.version_id,
                    document.artifact_id,
                    config.model_dump(),
                ]
            )
            registry.invalidate_views(document.document_id, except_key=key)
            cached = self._cached(key, document, config, records)
            if cached is not None:
                all_views.extend(cached)
                registry.set_view_state(key, document, config.model_dump(), "ready")
            else:
                pending.append((key, document, config, records))
        global_limit = int(os.getenv("RAG_VIEW_MAX_REQUESTS_PER_BUILD", "8"))
        needed = sum(
            math.ceil(len(records) / config.batch_size)
            for _, _, config, records in pending
        )
        for key, document, config, records in pending:
            local_usage = dict.fromkeys(usage, 0)
            try:
                if (
                    needed > global_limit
                    or math.ceil(len(records) / config.batch_size) > config.max_requests
                ):
                    raise ValueError(
                        "View generation request budget exceeded before any paid call"
                    )
                registry.set_view_state(key, document, config.model_dump(), "running")
                generator = RecordedGenerator(self._client(config), local_usage)
                views = []
                for start in range(0, len(records), config.batch_size):
                    views.extend(
                        generate_question_views(
                            records[start : start + config.batch_size], generator
                        )
                    )
                validate_views(views, records)
                payload = {
                    "document_id": document.document_id,
                    "version_id": document.version_id,
                    "artifact_id": document.artifact_id,
                    "config": config.model_dump(),
                    "views": [v.model_dump() for v in views],
                    "usage": local_usage,
                }
                self.root.mkdir(parents=True, exist_ok=True)
                temporary = self.root / ("." + uuid4().hex + ".tmp")
                try:
                    temporary.write_text(
                        json.dumps(
                            {"sha256": digest(payload), "payload": payload},
                            ensure_ascii=False,
                        ),
                        encoding="utf-8",
                    )
                    temporary.replace(self.root / (key + ".json"))
                finally:
                    temporary.unlink(missing_ok=True)
                registry.set_view_state(
                    key, document, config.model_dump(), "ready", usage=local_usage
                )
                all_views.extend(views)
            except Exception as exc:
                registry.set_view_state(
                    key,
                    document,
                    config.model_dump(),
                    "failed",
                    error=str(exc)[:1000],
                    usage=local_usage,
                )
                if config.failure_policy == "fail_build":
                    raise
            finally:
                for name in usage:
                    usage[name] += local_usage[name]
                self.metrics["view_usage"] = dict(usage)
        if all_views:
            # Reuse the current embedding/cache path, not a second uncontrolled encoder.
            try:
                built = IndexingPipeline(embed, self.store_factory).build_views(
                    snapshot, all_views, model_name=self.model_name
                )
                snapshot.view_store, snapshot.view_model_name = (
                    built.view_store,
                    built.view_model_name,
                )
            except Exception as exc:
                if any(
                    self.resolved_config(
                        registry.get_document(d.document_id).view_config
                    ).failure_policy
                    == "fail_build"
                    for d in snapshot.documents
                    if registry.get_document(d.document_id).view_config.get("enabled")
                ):
                    raise
                self.metrics["view_index_error"] = type(exc).__name__
                all_views = []
        self.metrics.update(view_count=len(all_views), view_usage=usage)
