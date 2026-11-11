"""Loopback console authentication boundaries, without models or paid calls."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api import create_app
from app.bootstrap import create_services
from RAG.tests.support import FakeEmbedding

TOKEN = "local-console-tests-administrator-token"
HEADERS = {
    "Origin": "http://127.0.0.1",
    "X-Console-Request": "1",
    "Sec-Fetch-Site": "same-origin",
}
PATH = "/api/v1/console/session"


class LocalConsoleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="rag-console-auth-")
        self.addCleanup(self.tmp.cleanup)
        self.service = create_services(
            Path(self.tmp.name), admin_token=TOKEN, embedding_factory=FakeEmbedding
        )

    def client(self, enabled=True, peer="127.0.0.1", **kwargs):
        client = TestClient(
            create_app(self.service, with_mcp=False, local_console=enabled),
            base_url="http://127.0.0.1",
            client=(peer, 50000),
            **kwargs,
        )
        client.__enter__()
        self.addCleanup(client.__exit__, None, None, None)
        return client

    def test_local_browser_enters_without_token_and_can_manage_base(self):
        client = self.client()
        self.assertEqual(client.get("/api/v1/me").status_code, 401)
        response = client.post(PATH, headers=HEADERS)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(TOKEN, response.text)
        cookie = response.headers["set-cookie"].lower()
        for attribute in ("httponly", "samesite=strict", "path=/api/"):
            self.assertIn(attribute, cookie)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertTrue(client.get("/api/v1/me", headers=HEADERS).json()["admin"])
        created = client.post(
            "/api/v1/knowledge-bases", headers=HEADERS, json={"name": "Local console"}
        )
        self.assertEqual(created.status_code, 201)
        self.assertEqual(
            client.delete(
                "/api/v1/knowledge-bases/" + created.json()["id"] + "?confirm=true",
                headers=HEADERS,
            ).status_code,
            200,
        )

    def test_cookie_requires_same_origin_custom_header_and_never_authenticates_mcp(
        self,
    ):
        client = self.client()
        self.assertEqual(client.post(PATH, headers=HEADERS).status_code, 200)
        self.assertEqual(client.get("/api/v1/me").status_code, 401)
        self.assertEqual(
            client.get(
                "/api/v1/me", headers={**HEADERS, "Origin": "http://attacker.example"}
            ).status_code,
            403,
        )
        self.assertEqual(
            client.get(
                "/api/v1/me", headers={**HEADERS, "Sec-Fetch-Site": "cross-site"}
            ).status_code,
            401,
        )
        self.assertEqual(
            client.get(
                "/api/v1/me", headers={**HEADERS, "Authorization": "Bearer invalid"}
            ).status_code,
            401,
        )
        self.assertEqual(client.get("/mcp/", headers=HEADERS).status_code, 401)

    def test_bootstrap_rejects_missing_origin_foreign_origin_and_remote_peer(self):
        client = self.client()
        for headers in (
            {},
            {"X-Console-Request": "1"},
            {"Origin": "http://127.0.0.1"},
            {**HEADERS, "Origin": "http://other.example"},
            {**HEADERS, "Sec-Fetch-Site": "same-site"},
        ):
            self.assertEqual(client.post(PATH, headers=headers).status_code, 403)
        self.assertEqual(client.get(PATH, headers=HEADERS).status_code, 405)
        self.assertEqual(
            client.post(PATH, headers={**HEADERS, "Host": "other.example"}).status_code,
            403,
        )
        # Even a configured external origin cannot mint a desktop session.
        with patch.dict("os.environ", {"RAG_ALLOWED_ORIGINS": "http://other.example"}):
            other = TestClient(
                create_app(self.service, with_mcp=False, local_console=True),
                base_url="http://127.0.0.1",
                client=("192.0.2.12", 50000),
            )
        self.assertEqual(other.post(PATH, headers=HEADERS).status_code, 403)
        self.assertEqual(
            other.post(
                PATH, headers={**HEADERS, "Origin": "http://other.example"}
            ).status_code,
            403,
        )

    def test_logout_and_restart_invalidate_cookie_without_affecting_api_token(self):
        client = self.client()
        client.post(PATH, headers=HEADERS)
        old_cookie = client.cookies.get("rag_local_console")
        self.assertEqual(client.delete(PATH, headers=HEADERS).status_code, 200)
        headers = {**HEADERS, "Cookie": "rag_local_console=" + old_cookie}
        self.assertEqual(client.get("/api/v1/me", headers=headers).status_code, 401)
        self.assertEqual(
            client.get(
                "/api/v1/me", headers={"Authorization": "Bearer " + TOKEN}
            ).status_code,
            200,
        )
        client.post(PATH, headers=HEADERS)
        current = client.cookies.get("rag_local_console")
        # A restarted server uses a new process-local session secret.
        from starlette.requests import Request
        from app.api.console_session import ConsoleSession

        req = Request(
            {
                "type": "http",
                "method": "GET",
                "scheme": "http",
                "path": "/api/v1/me",
                "query_string": b"",
                "headers": [
                    (b"host", b"127.0.0.1"),
                    (b"x-console-request", b"1"),
                    (b"cookie", ("rag_local_console=" + current).encode()),
                ],
                "client": ("127.0.0.1", 50000),
                "server": ("127.0.0.1", 80),
            }
        )
        self.assertFalse(ConsoleSession(enabled=True).authenticate(req))

    def test_remote_serve_stays_authenticated_by_default(self):
        client = self.client(enabled=False)
        self.assertEqual(client.post(PATH, headers=HEADERS).status_code, 404)
        self.assertEqual(client.get("/api/v1/me", headers=HEADERS).status_code, 401)
        self.assertEqual(
            client.get(
                "/api/v1/me", headers={"Authorization": "Bearer " + TOKEN}
            ).status_code,
            200,
        )
        with patch(
            "sys.argv", ["rag-service", "serve", "--host", "0.0.0.0", "--local-console"]
        ):
            from app.cli import main

            with self.assertRaises(SystemExit) as result:
                main()
        self.assertEqual(result.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
