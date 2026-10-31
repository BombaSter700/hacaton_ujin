import logging
from time import perf_counter

from fastapi import Request

logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next):
    started = perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Process-Time"] = f"{perf_counter() - started:.6f}"
        return response
    finally:
        # Route template avoids secrets in path parameters; never record headers/query/body.
        route = request.scope.get("route")
        path = getattr(route, "path", "<unmatched>")
        logger.info(
            "Request %s %s status=%s duration=%.4fs",
            request.method,
            path,
            status_code,
            perf_counter() - started,
        )
