from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
    is_current: bool = False
    created_at: datetime
    last_activity_at: datetime
    expires_at: datetime


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]
    total: int


class SessionRevokeResponse(BaseModel):
    success: bool
