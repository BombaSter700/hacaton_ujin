from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database.session import get_db
from app.core.dependencies.auth import get_current_user
from app.core.limiter import limiter
from app.schemas.user import (
    LoginRequest,
    RefreshRequest,
    Token,
    UserCreate,
    UserResponse,
)
from app.services.session_service import (
    create_session,
    revoke_session,
    rotate_refresh_token,
)
from app.services.user_service import (
    authenticate_user,
    create_access_token,
    register_user,
)

router = APIRouter()


def token_response(user, session, refresh_token):
    expires = session.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    return Token(
        access_token=create_access_token(user, session),
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        refresh_expires_in=max(
            0, int((expires - datetime.now(timezone.utc)).total_seconds())
        ),
    )


@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("3/minute")
def register(request: Request, data: UserCreate, db: Session = Depends(get_db)):
    return UserResponse.from_user(register_user(db, data))


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data)
    session, refresh_token = create_session(db, user)
    return token_response(user, session, refresh_token)


@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
def refresh(request: Request, data: RefreshRequest, db: Session = Depends(get_db)):
    session, refresh_token = rotate_refresh_token(db, data.refresh_token)
    return token_response(session.user, session, refresh_token)


@router.post("/logout", status_code=204)
def logout(
    request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    revoke_session(db, request.state.auth_session.id, user.id)
    return Response(status_code=204)


@router.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_user)):
    return UserResponse.from_user(user)
