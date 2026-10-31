"""Validate the current auth session; never trust caller-provided identity headers."""

from enum import Enum
from typing import Any

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings

security = HTTPBearer(auto_error=False)


class UserRole(str, Enum):
    ADMIN = "admin"
    CLIENT = "client"


async def auth_http_client():
    async with httpx.AsyncClient(
        base_url=settings.auth_service_url,
        timeout=settings.auth_timeout_seconds,
        trust_env=False,
    ) as client:
        yield client


async def get_user_info(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    client: httpx.AsyncClient = Depends(auth_http_client),
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(
            401, "Bearer token is required", headers={"WWW-Authenticate": "Bearer"}
        )
    try:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer " + credentials.credentials},
        )
    except httpx.HTTPError:
        raise HTTPException(503, "Authentication service unavailable") from None
    if response.status_code in (401, 403):
        raise HTTPException(response.status_code, "Invalid or revoked session")
    if response.status_code != 200:
        raise HTTPException(503, "Authentication service unavailable")
    try:
        user = response.json()
        valid = (
            isinstance(user, dict)
            and type(user.get("id")) is int
            and user["id"] > 0
            and user.get("role") in ("admin", "client")
            and user.get("is_active") is True
        )
    except (ValueError, TypeError):
        valid = False
    if not valid:
        raise HTTPException(503, "Invalid response from authentication service")
    # No object ACL exists yet. Do not expose all organizations/devices to clients.
    if user["role"] != "admin":
        raise HTTPException(
            403, "IoT access is currently available to administrators only"
        )
    return {"user_id": user["id"], "role": user["role"]}


get_user_from_auth = get_user_info
get_user_from_jwt = get_user_info


def require_any_role(required_roles: list[str]):
    def checker(user_info: dict = Depends(get_user_info)):
        if user_info["role"] not in required_roles:
            raise HTTPException(403, "Insufficient permissions")
        return user_info

    return checker


def require_role(required_role: str):
    return require_any_role([required_role])


require_admin = require_role("admin")
require_client_or_admin = require_any_role(["admin", "client"])
