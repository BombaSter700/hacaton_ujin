# Ujin IoT Management Platform

Хакатонный проект веб-приложения для управляющей компании: единая панель для работы с IoT-устройствами жилых объектов.

## Сервисы

- `backend/auth` — сервис авторизации и управления доступом.
- `backend/integration` — сервис интеграции с платформой Ujin и другими IoT-системами.
- `backend/emulators` — эмуляторы устройств и локальные инструменты для разработки и демонстрации интеграций.
- `frontend/admin-panel` — веб-панель УК.
- `infra` — инфраструктурные скрипты.

Сервисы разрабатываются независимо и взаимодействуют через API. Сейчас проект находится на стадии каркасов и хакатонного прототипа; наличие каталога сервиса не означает, что он уже готов к запуску.

## Документация

См. [каталог документации](docs/README.md), включая [быстрый старт эмулятора](docs/iot-hackathon/quickstart.md) и материалы по API и протоколу Ujin.

## Локальные файлы

`.env`, `env.example`, `доступы.json` и `programmisto.pdf` оставлены в корне: в них могут находиться локальная конфигурация, доступы или исходные материалы команды. Не добавляйте секреты в Git.

## Local Docker infrastructure

```powershell
docker compose up -d --wait
docker compose ps
curl.exe --fail http://localhost:8080/__health
```

The default stack runs PostgreSQL 18, KrakenD, Redis 7, ClickHouse 25.3 and a fleet
of nine IoT emulators. Fleet health: `http://localhost:8098/health`; device ports:
8099–8107. See the [infrastructure guide](docs/infrastructure/README.md) and
[integration contract](docs/infrastructure/emulators/README.md).
The gateway has no API
routes yet; `/__health` checks the gateway itself. PostgreSQL creates
`auth_db` and `integration_db` on the first start with an empty volume.
Local defaults work with an empty `.env`. Override `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `POSTGRES_DB` and `KRAKEND_PORT` there if needed.
The default password is for local development only. PostgreSQL is not
published to the host; the gateway binds to localhost.

Unfinished applications use the `backend` and `frontend` profiles and are
excluded from the default startup. These profiles are not ready to run:
backend still needs missing app modules, shared code and Alembic configuration
and migrations; frontend needs its Dockerfile and Nuxt modules.
Once implemented, enable them with `--profile backend --profile frontend`.

Stop containers while preserving data: `docker compose down`.

### IoT storage

- PostgreSQL: users, administrators, roles, organizations, buildings and device registry.
- ClickHouse: `iot.telemetry` (numeric readings, 30 days), `iot.device_events`
  (alarms and command results, one year), `iot.audit_events` (service audit, two years).
- Redis: latest device state and future ingestion streams; AOF enabled with
  `appendfsync everysec`. An OS/power failure may lose about one second of writes.
  `noeviction` prevents silent removal of queue entries; producers must handle
  memory-limit errors and consumers must acknowledge only after durable writes.

Internal addresses: `programmisto_clickhouse:8123` (HTTP),
`programmisto_clickhouse:9000` (native), `programmisto_redis:6379`.
ClickHouse ports are not published. Redis binds to localhost on the host.
Local defaults: `CLICKHOUSE_USER=ujin`, `CLICKHOUSE_DB=iot`,
`CLICKHOUSE_PASSWORD=local-clickhouse-password`, `REDIS_PASSWORD=local-redis-password`.
Override these through `.env` for shared environments.

ClickHouse initialization runs only on an empty data volume. Re-running
`bash /docker-entrypoint-initdb.d/init-databases.sh` inside the container is safe
for adding missing tables/indexes, but is NOT a schema migration: `IF NOT EXISTS`
does not update existing column types, keys or TTLs. Do not delete data volumes
to apply schema changes. TTL cleanup and ReplacingMergeTree deduplication happen
asynchronously. Queries requiring immediate deduplication must use `FINAL` or
an equivalent event/version-aware aggregation. Replays must retain the same
organization/device/metric/event ID and measurement timestamp. Ingestion must
validate timestamps and tenant access before inserting. No rollup tables are
created yet; their retention must be designed before extending raw history.

`context` and `payload` are JSON-encoded strings validated by the application.
The device registry and access checks remain in PostgreSQL/API; ClickHouse does
not enforce those cross-database relationships. UUID identifiers are the initial
schema convention and should be agreed with the application team.

Storage smoke check (includes a restart of Redis and ClickHouse):

```powershell
python scripts/smoke-infrastructure.py
```

This creates a dedicated `_infrastructure_smoke` table and a Redis key,
verifies persistence across restart and removes those test artifacts on success.
It does not start application services or benchmark ingestion throughput.
