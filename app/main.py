"""ASGI factory: uvicorn app.main:create_app --factory. Prefer the rag-service CLI."""

from app.api import create_app

__all__ = ["create_app"]
