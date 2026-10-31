# app/api/v1/__init__.py
from fastapi import APIRouter

from endpoints import integrations, devices, commands

api_router = APIRouter()

# Подключаем их к общему API
api_router.include_router(integrations.router)
api_router.include_router(devices.router)
api_router.include_router(commands.router)