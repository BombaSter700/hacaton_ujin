"""Email/password login and public registration with a fixed client role."""

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import InvalidCredentialsException, UserAlreadyExistsException
from app.models import User, UserProfile

pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=True
)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def register_user(db: Session, data):
    user = User(
        email=str(data.email).lower(),
        hashed_password=get_password_hash(data.password),
        role="client",
    )
    user.profile = UserProfile(
        first_name=data.first_name, last_name=data.last_name, phone=data.phone
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise UserAlreadyExistsException() from exc
    db.refresh(user)
    return user


def authenticate_user(db: Session, data):
    user = db.scalar(select(User).where(User.email == str(data.email).lower()))
    if (
        user is None
        or not verify_password(data.password, user.hashed_password)
        or not user.is_active
    ):
        raise InvalidCredentialsException()
    return user


def create_access_token(user, session):
    return jwt.encode(
        {
            "sub": str(user.id),
            "role": user.role,
            "session_token": session.session_token,
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.access_token_expire_minutes),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def update_profile(db: Session, user, data):
    if user.profile is None:
        user.profile = UserProfile()
    for name, value in data.model_dump(exclude_unset=True).items():
        setattr(user.profile, name, value)
    db.commit()
    db.refresh(user)
    return user
