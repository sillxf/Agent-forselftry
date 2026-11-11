"""Explicit administration; no implicit migration or paid model probe at startup."""

import argparse, json, os, secrets
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(prog="rag-service")
    parser.add_argument(
        "--data",
        default=os.getenv("RAG_SERVICE_DATA", str(Path.home() / ".rag-service")),
    )
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("init")
    serve = subs.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8090)
    worker = subs.add_parser("worker")
    worker.add_argument("--once", action="store_true")
    subs.add_parser("mcp-stdio")
    backup = subs.add_parser("backup")
    backup.add_argument("destination")
    restore = subs.add_parser("restore")
    restore.add_argument("backup")
    restore.add_argument("destination")
    migrate = subs.add_parser("migrate-legacy")
    migrate.add_argument("--knowledge", required=True)
    migrate.add_argument("--storage", required=True)
    migrate.add_argument("--backup", required=True)
    migrate.add_argument("--writers-stopped", action="store_true")
    args = parser.parse_args()
    root = Path(args.data).resolve()
    if args.command == "mcp-stdio":
        from rag_service.mcp import stdio

        stdio()
        return
    if args.command == "restore":
        from rag_service.maintenance import restore_service

        print(
            json.dumps(
                restore_service(args.backup, args.destination),
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if args.command == "init":
        root.mkdir(parents=True, exist_ok=True, mode=0o700)
        token = root / "admin.token"
        if not token.exists() and not os.getenv("RAG_SERVICE_ADMIN_TOKEN"):
            with token.open("x", encoding="utf-8") as f:
                f.write(secrets.token_urlsafe(40))
            token.chmod(0o600)
        from rag_service.service import RAGService

        service = RAGService(root)
        if not service.catalog.list_kbs():
            service.catalog.create_kb(
                {"name": "My knowledge", "description": "Default knowledge base"}
            )
        print(
            json.dumps(
                {
                    "data": str(root),
                    "admin_token_file": str(token),
                    "knowledge_bases": service.catalog.list_kbs(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if args.command == "backup":
        from rag_service.maintenance import backup_service

        backup_service(root, args.destination)
        print("Backup verified: " + str(Path(args.destination).resolve()))
        return
    from rag_service.service import RAGService

    service = RAGService(root)
    if args.command == "serve":
        import uvicorn
        from rag_service.api import create_app

        uvicorn.run(create_app(service), host=args.host, port=args.port)
    elif args.command == "worker":
        from rag_service.worker import Worker

        Worker(service).run(once=args.once)
    elif args.command == "migrate-legacy":
        from rag_service.maintenance import migrate_legacy

        print(
            json.dumps(
                migrate_legacy(
                    service,
                    args.knowledge,
                    args.storage,
                    args.backup,
                    writers_stopped=args.writers_stopped,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
