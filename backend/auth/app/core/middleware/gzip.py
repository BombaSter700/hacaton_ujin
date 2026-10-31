from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware


def setup_gzip_middleware(app: FastAPI) -> None:
    """Setup Gzip compression middleware for the application."""
    app.add_middleware(GZipMiddleware, minimum_size=1000)
