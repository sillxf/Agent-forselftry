"""Application errors shared by transports and domain services."""


class AccessDenied(PermissionError):
    pass


class BusyError(RuntimeError):
    pass


class RateLimited(Exception):
    """A key used up its per-minute quota (429).

    Not a PermissionError: Python raises that for locked or read-only files too,
    and a Windows file lock during deletion was reported to callers as a rate limit.
    """


class InvalidRequest(ValueError):
    """The caller's input is wrong (422): a bad filter, timestamp or filename."""


class NotPublished(ValueError):
    """No publication can serve this request yet (409): build and publish first."""


class IndexIntegrityError(ValueError):
    """Index or registry data is missing or inconsistent (503): restore or rebuild.

    Subclasses ValueError so the existing recovery paths that catch it still work.
    """
