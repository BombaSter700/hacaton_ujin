"""Public error responses never include credentials, request bodies or stack traces."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.core.exceptions import AuthException

logger = logging.getLogger(__name__)


async def auth_exception_handler(request: Request, exc: AuthException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code},
        headers=exc.headers,
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail}, headers=exc.headers
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Pydantic error input/ctx may contain a password or token.
    errors = [
        {"loc": list(error["loc"]), "type": error["type"], "msg": "Invalid value"}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors})


async def unexpected_exception_handler(request: Request, exc: Exception):
    # Do not log the exception string: database exceptions may embed parameters.
    logger.error("Unhandled request failure (%s)", type(exc).__name__)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"},
    )


def setup_auth_error_handling(app: FastAPI):
    app.add_exception_handler(AuthException, auth_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unexpected_exception_handler)


async def error_handling_middleware(request: Request, call_next):
    """Compatibility wrapper; prefer registered exception handlers."""
    try:
        return await call_next(request)
    except AuthException as exc:
        return await auth_exception_handler(request, exc)
    except HTTPException as exc:
        return await http_exception_handler(request, exc)
    except Exception as exc:
        return await unexpected_exception_handler(request, exc)
