from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database.session import get_db
from app.core.dependencies.auth import get_current_user
from app.schemas.session import (
    SessionListResponse,
    SessionResponse,
    SessionRevokeResponse,
)
from app.services.session_service import get_user_sessions, revoke_session

router = APIRouter()


@router.get("/", response_model=SessionListResponse)
def list_sessions(
    request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    current = request.state.auth_session.id
    sessions = [
        SessionResponse.model_validate(session).model_copy(
            update={"is_current": session.id == current}
        )
        for session in get_user_sessions(db, user.id)
    ]
    return SessionListResponse(sessions=sessions, total=len(sessions))


@router.delete("/{session_id}", response_model=SessionRevokeResponse)
def revoke(
    session_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    if not revoke_session(db, session_id, user.id):
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionRevokeResponse(success=True)
