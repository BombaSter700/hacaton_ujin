"""Opt-in local Compose smoke: python backend/integration/tests/smoke_gateway.py.

Creates a disposable admin and fleet metadata, changes/restores thermostat target.
Requires the local Compose stack; never points at production.
"""
import json
import secrets
import subprocess
import time
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def container(service, code):
    result = subprocess.run(
        ["docker", "compose", "exec", "-T", service, "python", "-c", code],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def request(path, token=None, data=None, expected=200):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = Request("http://localhost:8080/api/v1" + path,
                  data=json.dumps(data).encode() if data is not None else None,
                  headers=headers)
    try:
        with urlopen(req, timeout=30) as response:
            status, body = response.status, response.read()
    except HTTPError as exc:
        status, body = exc.code, exc.read()
    assert status == expected, (path, status, body.decode()[:300])
    return json.loads(body) if body else None


def main():
    email = "iot-smoke-" + secrets.token_hex(8) + "@example.com"
    password = secrets.token_urlsafe(24)
    org, obj = str(uuid.uuid4()), str(uuid.uuid4())
    token = None
    device_id = None
    original = None
    try:
        request("/auth/register", data={"email": email, "password": password}, expected=201)
        tokens = request("/auth/login", data={"email": email, "password": password})
        token = tokens["access_token"]
        request("/devices/" + str(uuid.uuid4()) + "/state", expected=401)
        request("/integrations/emulators/sync", token, {"organization_id": org, "object_id": obj}, expected=403)
        container("programmisto_auth", f"from app.core.database.session import SessionLocal; from app.models.user import User; db=SessionLocal(); u=db.query(User).filter_by(email={email!r}).one(); u.role='admin'; db.commit(); db.close()")
        result = request("/integrations/emulators/sync", token, {"organization_id": org, "object_id": obj})
        assert result["devices_count"] == 9, result
        request("/integrations/emulators/sync", token, {"organization_id": org, "object_id": obj})
        devices = request("/devices/?object_id=" + obj, token)
        assert len(devices) == 9
        device = next(d for d in devices if d["device_type"] == "thermostat")
        device_id = device["id"]
        signal = next(s for s in device["signals"] if s["external_signal_id"] == "target_temp")
        assert signal["is_writable"]
        deadline = time.monotonic() + 30
        while True:
            state = request(f"/devices/{device_id}/state", token)
            if "target_temp" in state["signals"]:
                break
            assert time.monotonic() < deadline, state
            time.sleep(2)
        original = state["signals"]["target_temp"]
        value = 24 if original != 24 else 23
        payload = {"signal_id": signal["id"], "value": value, "idempotency_key": str(uuid.uuid4())}
        command = request(f"/commands/{device_id}/send", token, payload)
        assert command["status"] == "success", command
        repeated = request(f"/commands/{device_id}/send", token, payload)
        assert repeated["command_id"] == command["command_id"]
        request(f"/commands/{device_id}/send", token, {**payload, "value": value + 1}, expected=409)
        request(f"/commands/{device_id}/send", token, {"signal_id": signal["id"], "value": 1000}, expected=400)
        deadline = time.monotonic() + 30
        while True:
            history = request(f"/devices/{device_id}/history?signal_name=target_temp&limit=100", token)
            if any(point["value"] == value for point in history):
                break
            assert time.monotonic() < deadline, history
            time.sleep(2)
        print("PASS: nine devices, state, confirmed command, idempotency, bounds and ClickHouse history")
    finally:
        try:
            if token and device_id and original is not None:
                request(f"/commands/{device_id}/send", token, {"signal_id": signal["id"], "value": original})
        finally:
            container("programmisto_integration", f"from uuid import UUID; from app.core.database.session import SessionLocal; from app.models.integration import Integration; from app.models.device import Device; from app.models.command_log import CommandLog; db=SessionLocal(); integrations=db.query(Integration).filter_by(organization_id=UUID({org!r})).all(); devices=db.query(Device).filter(Device.integration_id.in_([i.id for i in integrations])).all(); db.query(CommandLog).filter(CommandLog.device_id.in_([d.id for d in devices])).delete(synchronize_session=False); [db.delete(d) for d in devices]; db.flush(); [db.delete(i) for i in integrations]; db.commit(); db.close()")
            container("programmisto_auth", f"from app.core.database.session import SessionLocal; from app.models.user import User; db=SessionLocal(); u=db.query(User).filter_by(email={email!r}).first(); db.delete(u) if u else None; db.commit(); db.close()")
            print("Disposable account and metadata removed; thermostat restored")


if __name__ == "__main__":
    main()
