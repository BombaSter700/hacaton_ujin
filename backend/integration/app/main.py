"""Integration API with service-local configuration."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.api.v1 import api_router
from app.core.config import settings
from app.core.database.engine import engine
from app.core.middleware.cors import setup_cors_middleware
from app.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        engine.dispose()


app = FastAPI(
    title="Integration Service API",
    version=settings.app_version,
    docs_url="/api/docs" if settings.debug else None,
    redoc_url=None,
    openapi_url="/api/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)
setup_cors_middleware(app)
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(api_router, prefix="/api/v1")
Instrumentator().instrument(app).expose(app)
