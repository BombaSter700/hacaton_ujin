"""Auth application. Business routes still require their models and migrations."""

import asyncio
from contextlib import asynccontextmanager, suppress
import logging

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1 import api_router
from app.core.audit import AuditClient
from app.core.config import settings
from app.core.database.engine import engine
from app.core.limiter import limiter
from app.core.middleware import (
    setup_cors_middleware,
    setup_gzip_middleware,
    logging_middleware,
)
from app.core.middleware.error_handling import (
    setup_auth_error_handling,
    error_handling_middleware,
)
from app.routers import health

logger = logging.getLogger(__name__)


async def session_cleanup_task():
    from app.core.database.session import get_db_context
    from app.services.session_service import cleanup_expired_sessions

    while True:
        await asyncio.sleep(3600)
        try:
            # SQLAlchemy sessions are synchronous; run maintenance off the event loop.
            def cleanup():
                with get_db_context() as db:
                    cleanup_expired_sessions(db)

            await asyncio.to_thread(cleanup)
        except Exception:
            logger.error("Session cleanup failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.audit = AuditClient(settings.audit_service_url, source_service="auth")
    cleanup_task = None
    publisher = None
    try:
        if settings.notifications_enabled:
            from app.services.event_publisher import AuthEventPublisher
            from app.services.notification_integration import register_auth_service
            import app.services.event_publisher as publisher_module

            publisher = AuthEventPublisher(settings.rabbitmq_url)
            await publisher.connect(retries=5, delay=3.0)
            if not publisher.is_connected:
                raise RuntimeError("Notification publisher is unavailable")
            publisher_module.event_publisher = publisher
            await register_auth_service()
        else:
            logger.info("Notification delivery is disabled")
        cleanup_task = asyncio.create_task(session_cleanup_task())
        yield
    finally:
        if cleanup_task is not None:
            cleanup_task.cancel()
            with suppress(asyncio.CancelledError):
                await cleanup_task
        try:
            if publisher is not None:
                await publisher.close()
        finally:
            await app.state.audit.aclose()
            engine.dispose()


app = FastAPI(
    title=f"{settings.app_name} API",
    version=settings.app_version,
    docs_url="/api/docs" if settings.debug else None,
    redoc_url=None,
    openapi_url="/api/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
setup_cors_middleware(app)
setup_gzip_middleware(app)
setup_auth_error_handling(app)
app.middleware("http")(error_handling_middleware)
app.middleware("http")(logging_middleware)
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(api_router, prefix="/api/v1")
Instrumentator().instrument(app).expose(app)


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }
