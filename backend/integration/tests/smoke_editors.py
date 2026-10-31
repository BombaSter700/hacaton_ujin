"""Local-only Compose smoke for device descriptions and saved rules.

Run from repository root: python backend/integration/tests/smoke_editors.py
Creates and removes a disposable account, fleet metadata and scenario; sends no commands.
"""
import json
import secrets
import subprocess
import uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def container(service, code):
    subprocess.run(["docker", "compose", "exec", "-T", service, "python", "-c", code], check=True, capture_output=True, text=True)


def request(path, token=None, data=None, method=None, expected=200):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = Request("http://localhost:8080/api/v1" + path, headers=headers,
                  data=json.dumps(data).encode() if data is not None else None, method=method)
    try:
        with urlopen(req, timeout=30) as response:
            status, body = response.status, response.read()
    except HTTPError as error:
        status, body = error.code, error.read()
    assert status == expected, (path, status, body.decode()[:500])
    return json.loads(body) if body else None


def main():
    email, password = "editors-" + secrets.token_hex(8) + "@example.com", secrets.token_urlsafe(24)
    org, obj = str(uuid.uuid4()), str(uuid.uuid4())
    token = None
    try:
        request("/auth/register", data={"email": email, "password": password}, expected=201)
        token = request("/auth/login", data={"email": email, "password": password})["access_token"]
        request("/scenarios/?object_id=" + obj, expected=401)
        request("/scenarios/?object_id=" + obj, token, expected=403)
        container("programmisto_auth", f"from app.core.database.session import SessionLocal; from app.models.user import User; db=SessionLocal(); u=db.query(User).filter_by(email={email!r}).one(); u.role='admin'; db.commit(); db.close()")
        request("/integrations/emulators/sync", token, {"organization_id": org, "object_id": obj})
        devices = request("/devices/?object_id=" + obj, token)
        thermostat = next(d for d in devices if d["device_type"] == "thermostat")
        signal = next(s for s in thermostat["signals"] if s["external_signal_id"] == "target_temp")
        temperature = next(s for s in thermostat["signals"] if s["external_signal_id"] == "temperature")
        definition = {"name": "Custom thermostat", "signals": [{k: s[k] for k in ("id", "name", "value_type", "unit", "is_writable", "min_value", "max_value")} for s in thermostat["signals"]]}
        target = next(s for s in definition["signals"] if s["id"] == signal["id"])
        target.update(name="Custom target", min_value=18, max_value=28)
        saved = request(f"/devices/{thermostat['id']}/definition", token, definition, "PUT")
        assert saved["name"] == definition["name"]
        bad = json.loads(json.dumps(definition))
        next(s for s in bad["signals"] if s["id"] == temperature["id"])["is_writable"] = True
        request(f"/devices/{thermostat['id']}/definition", token, bad, "PUT", 422)
        request("/integrations/emulators/sync", token, {"organization_id": org, "object_id": obj})
        saved = request(f"/devices/{thermostat['id']}", token)
        assert saved["name"] == "Custom thermostat"
        assert next(s for s in saved["signals"] if s["id"] == signal["id"])["name"] == "Custom target"
        payload = {"name": "Day climate", "object_id": obj, "enabled": False, "match_mode": "all", "conditions": [
            {"kind": "time", "start_time": "22:00", "end_time": "06:00", "timezone": "Europe/Moscow"},
            {"kind": "signal", "device_id": thermostat["id"], "signal_id": temperature["id"], "operator": "lt", "value": 20}],
            "actions": [{"device_id": thermostat["id"], "signal_id": signal["id"], "value": 24}]}
        scenario = request("/scenarios/", token, payload, expected=201)
        path = "/scenarios/" + scenario["id"]
        assert request(path, token)["conditions"] == payload["conditions"]
        assert request("/scenarios/?object_id=" + obj, token)["total"] == 1
        scenario = request(path, token, {**payload, "name": "Edited climate", "expected_revision": scenario["revision"]}, "PUT")
        request(path, token, {**payload, "expected_revision": 1}, "PUT", 409)
        scenario = request(path, token, {"enabled": True, "expected_revision": scenario["revision"]}, "PATCH")
        assert scenario["enabled"]
        blocked = json.loads(json.dumps(definition))
        next(s for s in blocked["signals"] if s["id"] == signal["id"])["is_writable"] = False
        request(f"/devices/{thermostat['id']}/definition", token, blocked, "PUT", 409)
        for change in ({"object_id": str(uuid.uuid4())}, {"actions": [{"device_id": thermostat["id"], "signal_id": temperature["id"], "value": 24}]}, {"actions": [{"device_id": thermostat["id"], "signal_id": signal["id"], "value": 99}]}):
            request("/scenarios/", token, payload | change, expected=422)
        scenario = request(path, token, {"enabled": False, "expected_revision": scenario["revision"]}, "PATCH")
        request(path + "?expected_revision=" + str(scenario["revision"]), token, method="DELETE", expected=204)
        request(path, token, expected=404)
        print("PASS: saved descriptions survive import; scenarios create/read/update/toggle/delete; stale revision, cross-object, read-only, range and enabled-rule protections")
    finally:
        container("programmisto_integration", f"from uuid import UUID; from app.core.database.session import SessionLocal; from app.models.integration import Integration; from app.models.device import Device; from app.models.scenario import Scenario; db=SessionLocal(); db.query(Scenario).filter_by(object_id=UUID({obj!r})).delete(); integrations=db.query(Integration).filter_by(organization_id=UUID({org!r})).all(); devices=db.query(Device).filter(Device.integration_id.in_([i.id for i in integrations])).all(); [db.delete(d) for d in devices]; db.flush(); [db.delete(i) for i in integrations]; db.commit(); db.close()")
        container("programmisto_auth", f"from app.core.database.session import SessionLocal; from app.models.user import User; db=SessionLocal(); u=db.query(User).filter_by(email={email!r}).first(); db.delete(u) if u else None; db.commit(); db.close()")
        print("Disposable editor fixtures removed")


if __name__ == "__main__":
    main()
