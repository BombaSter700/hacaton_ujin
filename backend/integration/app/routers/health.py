from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.core.database.engine import engine
from app.services.state_repo import state_repo

router = APIRouter()


@router.get("")
@router.get("/live")
def live():
    return {"status": "ok", "service": "integration"}


@router.get("/ready")
async def ready():
    try:
        with engine.connect() as connection:
            for table in (
                "integrations",
                "devices",
                "signals",
                "command_logs",
                "device_event_logs",
                "scenarios",
            ):
                connection.execute(text(f"SELECT 1 FROM {table} WHERE false"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "database": "unavailable"},
        )
    try:
        if state_repo.redis is None:
            raise RuntimeError("Redis is not connected")
        await state_repo.redis.ping()
    except Exception:
        return JSONResponse(
            status_code=503, content={"status": "unavailable", "redis": "unavailable"}
        )
    return {"status": "ok", "database": "ok", "redis": "ok", "service": "integration"}
