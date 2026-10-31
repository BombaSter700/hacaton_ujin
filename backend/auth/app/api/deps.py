"""Compatibility exports for existing API routes."""

from app.core.dependencies.auth import (
    get_current_user,
    get_user_info,
    get_user_from_jwt,
    get_user_from_headers,
    require_role,
    require_any_role,
    require_admin,
    require_client_or_admin,
)

__all__ = [
    "get_current_user",
    "get_user_info",
    "get_user_from_jwt",
    "get_user_from_headers",
    "require_role",
    "require_any_role",
    "require_admin",
    "require_client_or_admin",
]
