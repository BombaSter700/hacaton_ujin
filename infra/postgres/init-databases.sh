#!/bin/bash

# Script to create databases for each service
# This script will be executed by the postgres container

set -euo pipefail

# Function to create database if it doesn't exist
create_database() {
    local db_name=$1
    if [ -n "$db_name" ]; then
        echo "Creating database: $db_name"
        psql -v ON_ERROR_STOP=1 --set=db_name="$db_name" \
            --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-'EOSQL'
            SELECT format('CREATE DATABASE %I', :'db_name')
            WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = :'db_name')\gexec
EOSQL
    fi
}

create_database "${AUTH_DB_NAME:-auth_db}"
create_database "${INTEGRATION_DB_NAME:-integration_db}"

echo "Database initialization completed"
