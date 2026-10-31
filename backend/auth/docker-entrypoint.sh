#!/bin/bash
set -e

echo "🔧 Auth Service Starting..."

RELOAD_FLAG=""
if [ "${UVICORN_RELOAD}" = "1" ]; then
  RELOAD_FLAG="--reload"
fi

# Ждем готовности PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
/wait-for-it.sh programmisto_postgres:5432 --timeout=60 --strict -- echo "✅ PostgreSQL is ready"


# Применяем миграции
echo "📝 Running database migrations..."
alembic upgrade head
echo "✅ Migrations completed"

# Запускаем основной сервис
echo "🚀 Starting Auth Service..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 ${RELOAD_FLAG}
