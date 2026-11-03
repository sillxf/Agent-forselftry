"""Application errors shared by transports and domain services."""


class AccessDenied(PermissionError):
    pass


class BusyError(RuntimeError):
    pass
