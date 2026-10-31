from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.core.database.engine import engine

router = APIRouter()


@router.get("")
@router.get("/live")
def live():
    return {"status": "ok", "service": "integration"}


@router.get("/ready")
def ready():
    try:
        with engine.connect() as connection:
            for table in (
                "integrations",
                "devices",
                "signals",
                "command_logs",
                "device_event_logs",
            ):
                connection.execute(text(f"SELECT 1 FROM {table} WHERE false"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "database": "unavailable"},
        )
    return {"status": "ok", "database": "ok", "service": "integration"}
