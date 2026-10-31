"""Authentication dependencies for Integration service."""

import sys

sys.path.append("/app/shared")

from typing import Any, Dict, List, Optional
from fastapi import Depends, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.exceptions.integration_exceptions import IntegrationAuthException
from core.auth.jwt import JWTValidator


security = HTTPBearer(auto_error=False)


def get_user_from_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """Extract user info from JWT token (optional, gateway-friendly)."""

    if not credentials:
        raise IntegrationAuthException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated (no token provided)",
        )

    try:
        validator = JWTValidator(settings)
        payload = validator.decode_token(credentials.credentials)

        return {
            "user_id": payload.get("sub"),
            "role": payload.get("role", "guest"),
        }

    except Exception:
        raise IntegrationAuthException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT token",
        )


def get_user_info(
    x_auth_id: Optional[str] = Header(None, alias="x-auth-id"),
    x_auth_role: Optional[str] = Header(None, alias="x-auth-role"),
    authorization: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """Extract user info from KrakenD headers with optional JWT decoding."""

    if not x_auth_id:
        raise IntegrationAuthException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated (missing x-auth-id header)",
        )

    session_token = None

    if authorization and authorization.startswith("Bearer "):
        try:
            token = authorization.split(" ")[1]
            validator = JWTValidator(settings)
            payload = validator.decode_token(token)
            session_token = payload.get("session_token")
        except Exception:
            pass

    return {
        "user_id": x_auth_id,
        "role": x_auth_role or "guest",
        "session_token": session_token,
    }


def require_role(required_role: str):
    """Require specific role."""

    def checker(user_info: Dict[str, Any] = Depends(get_user_info)) -> Dict[str, Any]:
        if user_info.get("role") != required_role:
            raise IntegrationAuthException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}",
            )
        return user_info

    return checker


def require_any_role(required_roles: List[str]):
    """Require one of allowed roles."""

    def checker(user_info: Dict[str, Any] = Depends(get_user_info)) -> Dict[str, Any]:
        if user_info.get("role") not in required_roles:
            raise IntegrationAuthException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(required_roles)}",
            )
        return user_info

    return checker


def require_admin(user_info: Dict[str, Any] = Depends(get_user_info)) -> Dict[str, Any]:
    """Require admin role."""
    return require_role("admin")(user_info)


def require_client_or_admin(
    user_info: Dict[str, Any] = Depends(get_user_info),
) -> Dict[str, Any]:
    """Require client or admin role."""
    return require_any_role(["client", "admin"])(user_info)
