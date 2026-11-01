#!/usr/bin/env sh
set -eu

# Просьба смотреть путь к файлу перед запуском, чтобы не запускать скрипт из другой директории.
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

docker compose version >/dev/null
docker compose -f docker-compose.yml --profile backend --profile frontend up -d --build --wait "$@"
docker compose -f docker-compose.yml --profile backend --profile frontend ps
