"""Authenticate bearer tokens and their exact server-side sessions."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database.session import get_db
from app.core.exceptions import (
    AuthException,
    InvalidTokenException,
    InsufficientPermissionsException,
)
from app.core.security.jwt import JWTValidator

security = HTTPBearer(auto_error=False)


def get_user_info(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    if credentials is None:
        raise InvalidTokenException("Bearer token is required")
    payload = JWTValidator().decode_token(credentials.credentials)
    return {
        "user_id": payload["sub"],
        "role": payload.get("role", "guest"),
        "session_token": payload.get("session_token"),
    }


def get_user_from_jwt(user_info: dict = Depends(get_user_info)):
    return user_info


def get_user_from_headers(user_info: dict = Depends(get_user_info)):
    """Compatibility name; identity headers never authenticate a request."""
    return user_info


def get_current_user(
    request: Request,
    user_info: dict = Depends(get_user_info),
    db: Session = Depends(get_db),
):
    from app.models.user import User
    from app.models.session import UserSession
    from app.services.session_service import update_session_activity

    session_token = user_info.get("session_token")
    if not session_token:
        raise InvalidTokenException("Token is not bound to a session")
    user = db.query(User).filter(User.id == int(user_info["user_id"])).first()
    if user is None:
        raise InvalidTokenException()
    if not user.is_active:
        raise AuthException(
            status_code=403, detail="Inactive user", error_code="INACTIVE_USER"
        )
    session = (
        db.query(UserSession)
        .filter(
            UserSession.session_token == session_token,
            UserSession.user_id == user.id,
            UserSession.is_active.is_(True),
            UserSession.expires_at > datetime.now(timezone.utc),
        )
        .first()
    )
    # Never fall back to another session through the user's refresh token.
    if session is None or session.requires_reauth:
        raise InvalidTokenException(
            "Session expired, revoked or requires re-authentication"
        )
    updated = update_session_activity(db, session_token, request)
    if updated is None or not updated.is_active or updated.requires_reauth:
        raise InvalidTokenException("Session revoked or requires re-authentication")
    return user


def require_any_role(required_roles: list[str]):
    allowed = frozenset(required_roles)

    def role_checker(user=Depends(get_current_user)):
        # Current database role wins over stale JWT claims.
        if user.role is None or user.role.name not in allowed:
            raise InsufficientPermissionsException()
        return user

    return role_checker


def require_role(required_role: str):
    return require_any_role([required_role])


require_admin = require_role("admin")
require_client_or_admin = require_any_role(["client", "admin"])
