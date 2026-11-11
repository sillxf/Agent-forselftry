"""The sole composition root: explicit, narrow domain dependencies."""

from dataclasses import dataclass
from pathlib import Path
import os
from app.storage.database import Database
from app.knowledge.catalog import KnowledgeBaseRepository
from app.knowledge.workspace import Workspaces
from app.knowledge.service import KnowledgeService
from app.knowledge.documents import DocumentService
from app.knowledge.inspection import DocumentInspectionService
from app.models.repository import ModelRepository
from app.models.providers import Providers
from app.models.service import ModelService
from app.permissions.repository import KeyRepository
from app.permissions.service import AccessControl
from app.audit.repository import AuditRepository
from app.indexing.repository import JobRepository
from app.indexing.service import IndexingService
from app.retrieval.factory import PipelineFactory
from app.retrieval.sessions import QuerySessions
from app.retrieval.service import RetrievalService
from app.core.config import RAG_EMBEDDING_MODEL, RAG_RERANKER_MODEL


@dataclass(frozen=True)
class Services:
    root: Path
    knowledge: KnowledgeService
    documents: DocumentService
    inspection: DocumentInspectionService
    retrieval: RetrievalService
    models: ModelService
    indexing: IndexingService
    access: AccessControl
    audit: AuditRepository
    workspaces: Workspaces


def create_services(
    root,
    *,
    admin_token=None,
    embedding_factory=None,
    reranker_factory=None,
    parser_factory=None,
):
    database = Database(root)
    token_file = database.root / "admin.token"
    token = (
        admin_token
        or os.getenv("RAG_SERVICE_ADMIN_TOKEN")
        or (token_file.read_text().strip() if token_file.exists() else "")
    )
    if len(token) < 24:
        raise ValueError(
            "Run rag-service init or set RAG_SERVICE_ADMIN_TOKEN (at least 24 characters)"
        )
    bases, models, audit = (
        KnowledgeBaseRepository(database),
        ModelRepository(database.connect),
        AuditRepository(database.connect),
    )
    keys = KeyRepository(database.connect, bases.kb)
    access = AccessControl(keys, bases, token, audit)
    jobs = JobRepository(database.connect, bases.kb)
    for identity, kind, provider, model in [
        (
            "default-embedding",
            "embedding",
            "sentence_transformers",
            RAG_EMBEDDING_MODEL,
        ),
        ("default-reranker", "reranker", "cross_encoder", RAG_RERANKER_MODEL),
    ]:
        try:
            models.model(identity)
        except KeyError:
            models.add_model(
                dict(kind=kind, provider=provider, model=model), identity=identity
            )
    providers = Providers(
        models, embedding_factory=embedding_factory, reranker_factory=reranker_factory
    )
    workspaces = Workspaces(database.root, bases.kb)
    factory = PipelineFactory(providers.embedding)
    sessions = QuerySessions(bases, workspaces, factory, providers)
    return Services(
        database.root,
        KnowledgeService(bases, models, workspaces, jobs, access, audit),
        DocumentService(workspaces, access, audit),
        DocumentInspectionService(workspaces, access),
        RetrievalService(
            bases,
            sessions,
            access,
            keys,
            audit,
            concurrency=int(os.getenv("RAG_SEARCH_CONCURRENCY", "4")),
        ),
        ModelService(models, providers, access, audit),
        IndexingService(
            database.root,
            jobs,
            bases,
            models,
            workspaces,
            providers,
            factory,
            access,
            audit,
            parser_factory,
        ),
        access,
        audit,
        workspaces,
    )
