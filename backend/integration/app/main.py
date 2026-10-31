"""
Интеграционный сервис Service - Main Application
"""
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.config import settings
from app.api.v1 import api_router
from app.routers import health
from app.core.database.session import create_tables
logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    """Manage application lifecycle using FastAPI lifespan."""
    print(f"🚀 {settings.app_name} v{settings.app_version} starting up...")
    print("📝 API Documentation: /api/docs")
    print("🏥 Health Check: /health")


   
# Create FastAPI app
app = FastAPI(
    title="Integration Service API",
    description="Сервис для интеграции с внешними системами, включая 1C и подобное.",
    version=settings.app_version,
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    openapi_url="/api/openapi.json",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    lifespan=lifespan,
)

# CORS is handled by KrakenD gateway, no need to set it here

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(api_router, prefix="/api/v1")

# Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
