from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database.session import get_db
from app.core.dependencies.auth import get_current_user, require_admin
from app.models import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import update_profile

router = APIRouter()


@router.get("/", response_model=list[UserResponse])
def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    users = db.scalars(select(User).order_by(User.id).offset(skip).limit(limit)).all()
    return [UserResponse.from_user(item) for item in users]


@router.patch("/me", response_model=UserResponse)
def edit_profile(
    data: UserUpdate, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    return UserResponse.from_user(update_profile(db, user, data))
