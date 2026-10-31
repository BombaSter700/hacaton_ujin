#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

set -a; source .env; source "$SCRIPT_DIR/.env"; set +a

BACKUP_DIR="$PROJECT_ROOT/$BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

echo "========================================"
echo "  MyMic Full Backup - $(date +%Y-%m-%d\ %H:%M:%S)"
echo "========================================"

"$SCRIPT_DIR/backup-postgres.sh" || echo "[WARN] Postgres backup failed"
"$SCRIPT_DIR/backup-clickhouse.sh" || echo "[WARN] ClickHouse backup failed"

echo "========================================"
echo "  Backup complete"
echo "  Location: $BACKUP_DIR"
echo "========================================"
