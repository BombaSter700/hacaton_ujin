#!/bin/sh
set -eu
python -m alembic upgrade head
if [ "${UVICORN_RELOAD:-0}" = "1" ]; then
    set -- --reload
else
    set --
fi
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-access-log "$@"
