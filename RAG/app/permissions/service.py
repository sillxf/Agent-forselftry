"""Authentication, scoped reads and administrator-only key management."""

import hmac
from app.core.exceptions import AccessDenied


class AccessControl:
    def __init__(self, keys, bases, token, audit):
        self.keys, self.bases, self.token, self.audit = keys, bases, token, audit

    def authenticate(self, token):
        if token and hmac.compare_digest(token, self.token):
            return {"id": "admin", "admin": True, "scopes": None}
        actor = self.keys.authenticate(token)
        if actor is None:
            raise AccessDenied("Valid service credentials required")
        return actor

    def authorize(self, actor, kb_id=None, *, admin=False):
        if admin and not actor["admin"]:
            raise AccessDenied("Administrator permission required")
        if kb_id is not None:
            if not actor["admin"] and kb_id not in actor["scopes"]:
                raise AccessDenied("Knowledge base access denied")
            return self.bases.kb(kb_id)

    def list(self, actor):
        self.authorize(actor, admin=True)
        return self.keys.keys()

    def create(self, actor, configuration):
        self.authorize(actor, admin=True)
        result = self.keys.create_key(configuration)
        self.audit.audit(actor["id"], "key_created", key_id=result["id"])
        return result

    def revoke(self, actor, identity):
        self.authorize(actor, admin=True)
        self.keys.revoke(identity)
        self.audit.audit(actor["id"], "key_revoked", key_id=identity)
        return {"revoked": True}
