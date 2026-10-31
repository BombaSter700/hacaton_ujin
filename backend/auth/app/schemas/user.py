from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UserCreate(RequestModel):
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=8, max_length=72, repr=False)
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    phone: str | None = Field(default=None, max_length=20)

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password exceeds bcrypt's 72-byte limit")
        return value


class UserUpdate(RequestModel):
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    phone: str | None = Field(default=None, max_length=20)


class UserResponse(BaseModel):
    id: int
    email: EmailStr = Field(max_length=254)
    role: Literal["admin", "client"]
    is_active: bool
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    @classmethod
    def from_user(cls, user):
        profile = user.profile
        return cls(
            id=user.id,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            first_name=profile.first_name if profile else None,
            last_name=profile.last_name if profile else None,
            phone=profile.phone if profile else None,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class LoginRequest(RequestModel):
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=1, max_length=72, repr=False)

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password exceeds bcrypt's 72-byte limit")
        return value


class RefreshRequest(RequestModel):
    refresh_token: str = Field(min_length=1, max_length=128, repr=False)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int
