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

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage application lifecycle using FastAPI lifespan."""
    print(f"🚀 {settings.app_name} v{settings.app_version} starting up...")
    print("📝 API Documentation: /api/docs")
    print("🏥 Health Check: /health")

    # Register with Notification Service and establish connection on startup.
    from app.services.notification_integration import (
        register_with_notification_service,
        notification_service,
    )
    from app.services.event_publisher import (
        initialize_integration_publisher,
        close_integration_publisher,
    )

    # Initialize AuditClient
    import sys

    sys.path.append("/app/shared")
    from core.audit import AuditClient

    try:
        app.state.audit = AuditClient(
            audit_url=settings.audit_service_url,
            source_service="integration",
        )
        logger.info("📋 AuditClient initialized")
    except Exception as e:
        logger.warning(f"⚠️  AuditClient init failed: {e}.")

    await register_with_notification_service()
    await notification_service.connect()
    await initialize_integration_publisher()

    print("✅ Service ready")

    try:
        yield
    finally:
        print(f"🛑 {settings.app_name} shutting down...")
        await close_integration_publisher()
        # Close notification service connection on shutdown.
        await notification_service.close()


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
