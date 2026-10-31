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
from app.services.analytics import analytics
logger = logging.getLogger("uvicorn")
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("⏳ Initializing database tables...")
    create_tables()
    logger.info("⏳ Initializing ClickHouse analytics...")
    analytics.connect()
    await analytics.start()

    logger.info(f"🚀 {settings.app_name} v{settings.app_version} starting up...")
    logger.info("📝 API Documentation: /api/docs")
    logger.info("🏥 Health Check: /health")

    try:
        yield
    finally:
        logger.info(f"🛑 {settings.app_name} shutting down...")
        await analytics.stop()
        logger.info("✅ Shutdown complete.")

   
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
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(api_router, prefix="/api/v1")

# Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
