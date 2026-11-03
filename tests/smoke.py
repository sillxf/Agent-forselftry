"""One bounded offline usability check; no benchmark, model download or paid call."""

from pathlib import Path
import json, tempfile
from fastapi.testclient import TestClient
from app.api import create_app
from app.bootstrap import create_services
from app.indexing.worker import Worker
from tests.support import FakeEmbedding, Parser

TOKEN = "local-smoke-administrator-token-not-a-real-secret"


def run():
    root = Path(tempfile.mkdtemp(prefix="independent-rag-smoke-"))
    service = create_services(
        root / "data",
        admin_token=TOKEN,
        embedding_factory=FakeEmbedding,
        parser_factory=lambda workspace, configuration: Parser(),
    )
    worker = Worker(service.indexing)
    admin = {"Authorization": "Bearer " + TOKEN}
    checks = []
    with TestClient(create_app(service), base_url="http://127.0.0.1") as client:
        assert client.get("/health/live").status_code == 200
        assert client.get("/").status_code == 200
        assert client.get("/api/v1/knowledge-bases").status_code == 401
        checks.append("startup-and-auth")

        def request(method, path, **kwargs):
            response = client.request(
                method, "/api/v1" + path, headers=kwargs.pop("headers", admin), **kwargs
            )
            assert response.is_success, (path, response.status_code, response.text)
            return response.json()

        kb = request(
            "POST",
            "/knowledge-bases",
            json={"name": "Smoke knowledge", "build": {"ocr_enabled": False}},
        )["id"]
        other = request("POST", "/knowledge-bases", json={"name": "Other knowledge"})[
            "id"
        ]
        uploaded = request(
            "POST",
            f"/knowledge-bases/{kb}/documents?filename=manual.md",
            content=b"Original failed login evidence and mitigation.",
        )
        document = uploaded["document"]["document_id"]
        first_version = uploaded["version"]["version_id"]

        def job(operation="build", **extra):
            queued = request(
                "POST",
                f"/knowledge-bases/{kb}/jobs",
                json={"operation": operation, **extra},
            )
            assert worker.run_once()
            completed = service.indexing.jobs.job(queued["id"])
            assert completed["status"] == "succeeded", completed.get("error")

        job()
        first = service.workspaces.get(kb).repository.current_pointer()["generation"]
        query = {
            "query": "failed login",
            "knowledge_base_ids": [kb],
            "top_k": 2,
            "include_trace": True,
        }
        response = request("POST", "/search", json=query)
        assert response["results"] and response["results"][0]["source"] == "manual.md"
        assert "source_path" not in response["results"][0]
        request("GET", f"/knowledge-bases/{kb}/documents/{document}")
        checks.append("upload-build-publish-search-inspect")
        request(
            "POST",
            f"/knowledge-bases/{kb}/documents?filename=manual.md&document_id={document}",
            content=b"Updated login mitigation and second version.",
        )
        job()
        job("rollback", generation_id=first)
        assert (
            service.workspaces.get(kb).repository.current_pointer()["generation"]
            == first
        )
        request(
            "POST",
            f"/knowledge-bases/{kb}/documents/{document}/restore-version",
            json={"version_id": first_version},
        )
        checks.append("versions-and-rollback")
        request("POST", f"/knowledge-bases/{kb}/documents/{document}/trash")
        assert request("POST", "/search", json=query)["results"] == []
        request("POST", f"/knowledge-bases/{kb}/documents/{document}/undelete")
        assert request("POST", "/search", json=query)["results"]
        key = request(
            "POST", "/keys", json={"name": "Smoke reader", "knowledge_base_ids": [kb]}
        )
        reader = {"Authorization": "Bearer " + key["token"]}
        assert (
            client.post(
                "/api/v1/search",
                json={**query, "knowledge_base_ids": [other]},
                headers=reader,
            ).status_code
            == 403
        )
        assert request("POST", "/search", json=query, headers=reader)["results"]
        request("DELETE", "/keys/" + key["id"])
        assert (
            client.post("/api/v1/search", json=query, headers=reader).status_code == 401
        )
        checks.append("delete-restore-scope-revoke")
        mcp = client.post(
            "/mcp/",
            headers={**admin, "Accept": "application/json, text/event-stream"},
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
        )
        assert mcp.status_code == 200, mcp.text
        assert len(mcp.json()["result"]["tools"]) == 6
        checks.append("mcp-tools")
        deleted = request(
            "DELETE", f"/knowledge-bases/{kb}/documents/{document}?confirm=true"
        )
        assert deleted["status"] == "completed"
        assert request("POST", "/search", json=query)["results"] == []
        checks.append("purge")
    from migrations.service_data import backup_service, restore_service

    backup_service(service.root, root / "backup")
    restore_service(root / "backup", root / "restored")
    restored = create_services(
        root / "restored", admin_token=TOKEN, embedding_factory=FakeEmbedding
    )
    assert len(restored.knowledge.repository.list_kbs()) == 2
    checks.append("backup-restore")
    return {"checks": checks, "paid_llm_calls": 0, "artifacts": str(root)}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False))
