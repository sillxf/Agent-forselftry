"""Process-local browser session for the explicitly enabled loopback console."""

import hmac
import ipaddress
import secrets

from fastapi.responses import JSONResponse


class ConsoleSession:
    cookie = "rag_local_console"

    def __init__(self, enabled=False):
        self.enabled = enabled
        self.secret = secrets.token_urlsafe(32)

    def trusted_browser(self, request, *, bootstrap=False):
        if not self.enabled or not request.client:
            return False
        try:
            if not ipaddress.ip_address(request.client.host).is_loopback:
                return False
        except ValueError:
            return False
        if request.url.hostname not in {"127.0.0.1", "localhost", "::1"}:
            return False
        if request.headers.get("x-console-request") != "1":
            return False
        origin = request.headers.get("origin")
        expected = f"{request.url.scheme}://{request.url.netloc}"
        if (bootstrap or origin) and origin != expected:
            return False
        site = request.headers.get("sec-fetch-site")
        return site is None or site == "same-origin"

    def authenticate(self, request):
        value = request.cookies.get(self.cookie, "")
        return (
            self.trusted_browser(request)
            and bool(value)
            and hmac.compare_digest(value, self.secret)
        )

    def handle(self, request):
        if not self.enabled:
            return JSONResponse({"detail": "Local console is disabled"}, 404)
        if not self.trusted_browser(request, bootstrap=True):
            return JSONResponse({"detail": "Local same-origin browser required"}, 403)
        if request.method == "POST":
            response = JSONResponse({"admin": True, "local_console": True})
            response.set_cookie(
                self.cookie,
                self.secret,
                httponly=True,
                samesite="strict",
                secure=request.url.scheme == "https",
                path="/api/",
            )
        elif request.method == "DELETE":
            self.secret = secrets.token_urlsafe(32)
            response = JSONResponse({"connected": False})
            response.delete_cookie(self.cookie, path="/api/")
        else:
            response = JSONResponse({"detail": "Method not allowed"}, 405)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
