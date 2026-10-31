"""Create, refresh and revoke simple server-side sessions."""

from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import InvalidTokenException
from app.models import UserSession


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(db: Session, user):
    refresh_token = secrets.token_urlsafe(32)
    session = UserSession(
        user_id=user.id,
        session_token=secrets.token_urlsafe(32),
        refresh_token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session, refresh_token


def rotate_refresh_token(db: Session, refresh_token: str):
    now = datetime.now(timezone.utc)
    session = db.scalar(
        select(UserSession)
        .where(
            UserSession.refresh_token_hash == hash_refresh_token(refresh_token),
            UserSession.is_active.is_(True),
            UserSession.expires_at > now,
        )
        .with_for_update()
    )
    if session is None or not session.user.is_active:
        raise InvalidTokenException("Invalid refresh token")
    new_token = secrets.token_urlsafe(32)
    session.refresh_token_hash = hash_refresh_token(new_token)
    session.last_activity_at = now
    db.commit()
    db.refresh(session)
    return session, new_token


def update_session_activity(db: Session, session_token: str, request=None):
    session = db.scalar(
        select(UserSession).where(
            UserSession.session_token == session_token,
            UserSession.is_active.is_(True),
            UserSession.expires_at > datetime.now(timezone.utc),
        )
    )
    if session is not None:
        session.last_activity_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(session)
    return session


def get_user_sessions(db: Session, user_id: int):
    return db.scalars(
        select(UserSession)
        .where(
            UserSession.user_id == user_id,
            UserSession.is_active.is_(True),
            UserSession.expires_at > datetime.now(timezone.utc),
        )
        .order_by(UserSession.created_at.desc())
    ).all()


def revoke_session(db: Session, session_id: int, user_id: int) -> bool:
    session = db.scalar(
        select(UserSession).where(
            UserSession.id == session_id,
            UserSession.user_id == user_id,
        )
    )
    if session is None:
        return False
    session.is_active = False
    db.commit()
    return True


def cleanup_expired_sessions(db: Session) -> int:
    from sqlalchemy import update

    result = db.execute(
        update(UserSession)
        .where(
            UserSession.expires_at <= datetime.now(timezone.utc),
            UserSession.is_active.is_(True),
        )
        .values(is_active=False)
    )
    db.commit()
    return result.rowcount
