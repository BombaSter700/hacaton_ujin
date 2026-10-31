"""Read-only checks for the VPS Compose and all uploaded bind-mount files."""

import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SERVICES = {
    "programmisto_auth",
    "programmisto_emulators",
    "programmisto_postgres",
    "programmisto_clickhouse",
    "programmisto_redis",
    "programmisto_krakend",
}
PAYLOAD = {
    "compose.staging.yml",
    "scripts/deploy-staging.sh",
    "infra/postgres/init-databases.sh",
    "infra/postgres/pg_hba.conf",
    "infra/clickhouse/init-databases.sh",
    "infra/krakend/krakend.tmpl",
    "infra/krakend/templates",
}


def main():
    env = {
        **os.environ,
        "IMAGE_TAG": "sha-" + "a" * 40,
        "DOCKER_REGISTRY": "ghcr.io/programmisto",
        "POSTGRES_PASSWORD": "validation-only-password",
        "REDIS_PASSWORD": "validation-only-password",
        "CLICKHOUSE_PASSWORD": "validation-only-password",
        "JWT_SECRET": "validation-only-key-" * 3,
        "AUTH_DATABASE_URL": "postgresql+psycopg2://ujin:validation@programmisto_postgres:5432/auth_db",
    }
    result = subprocess.run(
        [
            "docker",
            "compose",
            "--env-file",
            ".env.staging.example",
            "-f",
            "compose.staging.yml",
            "config",
            "--format",
            "json",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    plan = json.loads(result.stdout)
    if set(plan["services"]) != SERVICES:
        raise SystemExit("Unexpected staging service set")
    for name, service in plan["services"].items():
        if (
            "build" in service
            or "profiles" in service
            or not service.get("healthcheck")
        ):
            raise SystemExit(f"Staging must use ready images and healthchecks: {name}")
        for volume in service.get("volumes", []):
            if volume["type"] == "bind":
                source = Path(volume["source"]).resolve()
                relative = source.relative_to(ROOT).as_posix()
                if (
                    relative not in PAYLOAD
                    or not (
                        source.is_dir()
                        if relative == "infra/krakend/templates"
                        else source.is_file()
                    )
                    or not volume.get("read_only")
                ):
                    raise SystemExit(f"Invalid staging bind mount: {relative}")
        for port in service.get("ports", []):
            if port.get("host_ip") != "127.0.0.1":
                raise SystemExit("Staging host ports must bind to localhost")
    for file in PAYLOAD | {"backend/auth/alembic.ini"}:
        if not (ROOT / file).exists():
            raise SystemExit(f"Missing release/build file: {file}")
    if not (ROOT / "infra/krakend/templates/auth_story.tmpl").is_file():
        raise SystemExit("Missing auth route template")
    if plan["services"]["programmisto_auth"].get("volumes"):
        raise SystemExit("Auth must use code and migrations baked into the image")
    if not plan["services"]["programmisto_auth"]["image"].endswith(":sha-" + "a" * 40):
        raise SystemExit("Auth image does not use the requested release tag")
    print("PASS: staging images, six healthchecks, private ports and release payload")


if __name__ == "__main__":
    main()
