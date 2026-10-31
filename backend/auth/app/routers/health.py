from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.database.engine import engine

router = APIRouter()


@router.get("")
@router.get("/live")
def live():
    return {"status": "ok", "service": "auth"}


@router.get("/ready")
def ready():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "database": "unavailable"},
        )
    return {"status": "ok", "database": "ok"}
