from fastapi import APIRouter
from app.api.v1.endpoints import integrations, devices, commands, telemetry

api_router = APIRouter()
api_router.include_router(integrations.router)
api_router.include_router(devices.router)
api_router.include_router(commands.router)

api_router.include_router(telemetry.router)
