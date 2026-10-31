"""Integration owns its configuration; no runtime path manipulation or shared package."""

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class IntegrationServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        hide_input_in_errors=True,
    )

    app_name: str = "integration"
    app_version: str = "0.1.0"
    debug: bool = False
    database_url: str = Field(repr=False)
    db_pool_size: int = Field(default=5, ge=1)
    db_max_overflow: int = Field(default=10, ge=0)
    db_pool_timeout: int = Field(default=30, ge=1)
    db_pool_recycle: int = Field(default=1800, ge=1)
    jwt_secret: str = Field(min_length=32, repr=False)
    jwt_algorithm: Literal["HS256"] = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)
    cors_origins: list[str] = Field(default_factory=list)
    cors_allow_credentials: bool = True
    frontend_url: str = "http://localhost:3000"


    clickhouse_host: str = "clickhouse"
    clickhouse_port: int = Field(default=8123, ge=1, le=65535)
    clickhouse_user: str = "default"
    clickhouse_password: str = Field(default="", repr=False) # Скрываем пароль из логов
    clickhouse_db: str = "iot"
    
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value):
        try:
            url = make_url(value)
        except Exception:
            raise ValueError("DATABASE_URL must be a SQLAlchemy URL") from None
        if url.drivername not in (
            "postgresql",
            "postgresql+psycopg2",
            "sqlite",
            "sqlite+pysqlite",
        ):
            raise ValueError("Use synchronous PostgreSQL or SQLite")
        return value

    @field_validator("jwt_secret")
    @classmethod
    def validate_signing_key(cls, value):
        if len(value.encode("utf-8")) < 32 or not value.strip():
            raise ValueError(
                "JWT_SECRET must contain at least 32 bytes and cannot be blank"
            )
        return value

    @model_validator(mode="after")
    def validate_configuration(self):
        if self.cors_allow_credentials and "*" in self.cors_origins:
            raise ValueError("Credentialed CORS requires explicit origins")
        return self


settings = IntegrationServiceSettings()
