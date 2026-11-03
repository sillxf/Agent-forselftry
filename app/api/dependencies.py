"""HTTP dependency access only; authorization belongs to the permission service."""

from fastapi import Depends, Request


def actor(request: Request):
    return request.state.actor


def admin(request: Request, who=Depends(actor)):
    request.app.state.services.access.authorize(who, admin=True)
    return who
