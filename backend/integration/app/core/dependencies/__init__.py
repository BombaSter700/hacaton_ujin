"""Dependency exports for integration service."""

from .integration import (
    get_user_from_jwt,
    get_user_info,
    require_admin,
    require_any_role,
    require_client_or_admin,
    require_role,
)

__all__ = [
    "get_user_from_jwt",
    "get_user_info",
    "require_admin",
    "require_any_role",
    "require_client_or_admin",
    "require_role",
]
