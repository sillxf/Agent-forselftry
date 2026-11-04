"""Explicit administration; no implicit migration or paid model probe at startup."""

import argparse, json, os, secrets
from pathlib import Path
from dotenv import load_dotenv


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(prog="rag-service")
    parser.add_argument(
        "--data",
        default=os.getenv("RAG_SERVICE_DATA", str(Path.cwd() / "storage")),
    )
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("init")
    serve = subs.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8090)
    worker = subs.add_parser("worker")
    worker.add_argument("--once", action="store_true")
    worker.add_argument("--desktop-safe-start", action="store_true")
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
        from mcp_server.server import stdio

        stdio()
        return
    if args.command == "restore":
        from migrations.service_data import restore_service

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
        from app.bootstrap import create_services

        service = create_services(root)
        if not service.knowledge.repository.list_kbs():
            service.knowledge.repository.create_kb(
                {"name": "My knowledge", "description": "Default knowledge base"}
            )
        print(
            json.dumps(
                {
                    "data": str(root),
                    "admin_token_file": str(token),
                    "knowledge_bases": service.knowledge.repository.list_kbs(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if args.command == "backup":
        from migrations.service_data import backup_service

        backup_service(root, args.destination)
        print("Backup verified: " + str(Path(args.destination).resolve()))
        return
    from app.bootstrap import create_services

    service = create_services(root)
    if args.command == "serve":
        import uvicorn
        from app.api import create_app

        uvicorn.run(create_app(service), host=args.host, port=args.port)
    elif args.command == "worker":
        from app.indexing.worker import Worker

        Worker(service.indexing).run(
            once=args.once, desktop_safe_start=args.desktop_safe_start
        )
    elif args.command == "migrate-legacy":
        from migrations.service_data import migrate_legacy

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
