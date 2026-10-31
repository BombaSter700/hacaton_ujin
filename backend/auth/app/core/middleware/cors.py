from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def setup_cors_middleware(app: FastAPI) -> None:
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=settings.cors_allow_credentials,
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        )
