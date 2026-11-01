from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.health import router


def test_database_readiness():
    app = FastAPI()
    app.include_router(router, prefix="/health")
    with TestClient(app) as client:
        response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
