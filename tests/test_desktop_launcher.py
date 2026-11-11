import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)
LAUNCHER = ROOT / "scripts" / "desktop.ps1"
POWERSHELL = shutil.which("powershell.exe") or shutil.which("powershell")


@unittest.skipUnless(
    os.name == "nt" and POWERSHELL and PYTHON.is_file(),
    "Windows launcher integration test",
)
class DesktopLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="rag-desktop-launcher-")
        self.addCleanup(self.temporary.cleanup)
        self.data = Path(self.temporary.name) / "data"
        self.port = self.free_port()
        self.env = os.environ.copy()
        self.env["RAG_SERVICE_DATA"] = str(self.data)
        self.env.pop("RAG_SERVICE_ADMIN_TOKEN", None)

    @staticmethod
    def free_port():
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            return listener.getsockname()[1]

    def run_launcher(self, action, *, check=True):
        result = subprocess.run(
            [
                POWERSHELL,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(LAUNCHER),
                "-Action",
                action,
                "-Port",
                str(self.port),
                "-NoBrowser",
                "-Quiet",
            ],
            cwd=ROOT,
            check=False,
            env=self.env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
        if check:
            self.assertEqual(result.returncode, 0)
        return result

    def initialize_with_old_queue(self):
        initialized = subprocess.run(
            [str(PYTHON), "-m", "app", "--data", str(self.data), "init"],
            cwd=ROOT,
            env=self.env,
            capture_output=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(
            initialized.returncode,
            0,
            (initialized.stdout + initialized.stderr).decode("utf-8", errors="replace"),
        )
        code = """
import sys
from app.bootstrap import create_services
from app.core.contracts import JobRequest
service = create_services(sys.argv[1])
actor = service.access.authenticate(service.access.token)
kb_id = service.knowledge.repository.list_kbs()[0]["id"]
service.indexing.submit(actor, kb_id, JobRequest(operation="gc"))
"""
        queued = subprocess.run(
            [str(PYTHON), "-c", code, str(self.data)],
            cwd=ROOT,
            env=self.env,
            capture_output=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(
            queued.returncode,
            0,
            (queued.stdout + queued.stderr).decode("utf-8", errors="replace"),
        )

    def request_json(self, path, *, opener=None, method="GET", headers=None):
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=b"" if method != "GET" else None,
            method=method,
            headers=headers or {},
        )
        client = opener or urllib.request.build_opener()
        with client.open(request, timeout=5) as response:
            return response.status, json.loads(response.read())

    def test_start_reuses_processes_bootstraps_local_admin_and_holds_old_jobs(self):
        self.initialize_with_old_queue()
        try:
            self.run_launcher("Start")
            state_path = self.data / "desktop.json"
            state = json.loads(state_path.read_text(encoding="utf-8-sig"))
            server_pid, worker_pid = state["server"]["id"], state["worker"]["id"]

            status, _ = self.request_json("/health/live")
            self.assertEqual(status, 200)
            unauthorized = urllib.request.Request(
                f"http://127.0.0.1:{self.port}/api/v1/me",
                headers={"X-Console-Request": "1"},
            )
            with self.assertRaises(urllib.error.HTTPError) as denied:
                urllib.request.urlopen(unauthorized, timeout=5)
            self.assertEqual(denied.exception.code, 401)

            cookies = urllib.request.HTTPCookieProcessor()
            browser = urllib.request.build_opener(cookies)
            headers = {
                "Origin": f"http://127.0.0.1:{self.port}",
                "X-Console-Request": "1",
                "Sec-Fetch-Site": "same-origin",
            }
            status, session = self.request_json(
                "/api/v1/console/session", opener=browser, method="POST", headers=headers
            )
            self.assertEqual(status, 200)
            self.assertTrue(session["admin"])
            _, identity = self.request_json(
                "/api/v1/me", opener=browser, headers={"X-Console-Request": "1"}
            )
            self.assertTrue(identity["admin"])
            _, jobs = self.request_json(
                "/api/v1/jobs", opener=browser, headers={"X-Console-Request": "1"}
            )
            self.assertEqual(len(jobs), 1)
            self.assertEqual(jobs[0]["status"], "queued")
            self.assertTrue(jobs[0]["awaiting_confirmation"])

            self.run_launcher("Start")
            reused = json.loads(state_path.read_text(encoding="utf-8-sig"))
            self.assertEqual(reused["server"]["id"], server_pid)
            self.assertEqual(reused["worker"]["id"], worker_pid)

            self.run_launcher("Stop")
            self.assertFalse(state_path.exists())
            with socket.socket() as connection:
                self.assertNotEqual(connection.connect_ex(("127.0.0.1", self.port)), 0)
        finally:
            self.run_launcher("Stop", check=False)

    def test_start_does_not_take_over_another_process_port(self):
        with socket.socket() as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind(("127.0.0.1", self.port))
            listener.listen(1)
            result = self.run_launcher("Start", check=False)
            self.assertNotEqual(result.returncode, 0)
            with socket.create_connection(("127.0.0.1", self.port), timeout=2):
                pass
        self.assertFalse((self.data / "desktop.json").exists())


if __name__ == "__main__":
    unittest.main()
