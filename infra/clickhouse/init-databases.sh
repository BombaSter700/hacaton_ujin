#!/bin/bash

set -euo pipefail

CLICKHOUSE_USER="${CLICKHOUSE_USER:-default}"
CLICKHOUSE_PASSWORD="${CLICKHOUSE_PASSWORD:-}"
CLICKHOUSE_DB="${CLICKHOUSE_DB:-iot}"

# Database names are SQL identifiers, not arbitrary SQL fragments.
if [[ ! "$CLICKHOUSE_DB" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
    echo "Invalid CLICKHOUSE_DB: use letters, digits and underscores; start with a letter or underscore." >&2
    exit 1
fi

cli() {
    clickhouse-client \
        --host 127.0.0.1 \
        --user "$CLICKHOUSE_USER" \
        --password "$CLICKHOUSE_PASSWORD" \
        --multiquery \
        "$@"
}

echo ">>> [ClickHouse init] Creating database: ${CLICKHOUSE_DB}"

cli --query "
CREATE DATABASE IF NOT EXISTS ${CLICKHOUSE_DB};

-- Numeric/boolean readings; boolean values are represented as 0/1.
-- received_at is the ingestion version. Replays must preserve event_id and measured_at.
-- ReplacingMergeTree removes duplicates during merges, not immediately.
CREATE TABLE IF NOT EXISTS ${CLICKHOUSE_DB}.telemetry
(
    organization_id UUID,
    building_id UUID,
    device_id UUID,
    metric LowCardinality(String),
    event_id UUID,
    measured_at DateTime64(3, 'UTC'),
    received_at DateTime64(3, 'UTC') DEFAULT now64(3),
    value Float64,
    unit LowCardinality(String) DEFAULT '',
    quality LowCardinality(String) DEFAULT 'good',
    source LowCardinality(String) DEFAULT 'ujin'
)
ENGINE = ReplacingMergeTree(received_at)
PARTITION BY toYYYYMM(measured_at)
ORDER BY (organization_id, device_id, metric, measured_at, event_id)
TTL toDateTime(measured_at) + INTERVAL 30 DAY;

-- Discrete events: leak/fire alarms, connectivity and command results.
CREATE TABLE IF NOT EXISTS ${CLICKHOUSE_DB}.device_events
(
    organization_id UUID,
    building_id UUID,
    device_id UUID,
    event_id UUID,
    event_type LowCardinality(String),
    severity LowCardinality(String) DEFAULT 'info',
    occurred_at DateTime64(3, 'UTC'),
    received_at DateTime64(3, 'UTC') DEFAULT now64(3),
    payload String DEFAULT '{}'
)
ENGINE = ReplacingMergeTree(received_at)
PARTITION BY toYYYYMM(occurred_at)
ORDER BY (organization_id, device_id, occurred_at, event_id)
TTL toDateTime(occurred_at) + INTERVAL 1 YEAR;

CREATE TABLE IF NOT EXISTS ${CLICKHOUSE_DB}.audit_events
(
    -- Identity
    event_id        UUID,
    source_service  LowCardinality(String),

    -- Classification
    event_type      LowCardinality(String),
    severity        LowCardinality(String) DEFAULT 'info',

    -- Timing
    occurred_at     DateTime64(3, 'UTC'),
    received_at     DateTime64(3, 'UTC') DEFAULT now64(),

    -- Actor context
    actor_id        Nullable(String),
    actor_type      LowCardinality(Nullable(String)),

    -- Entity context
    entity_type     LowCardinality(Nullable(String)),
    entity_id       Nullable(String),

    -- Tracing
    trace_id        Nullable(UUID),

    -- JSON payload
    context         String DEFAULT '{}'
)
ENGINE = ReplacingMergeTree(received_at)
PARTITION BY toYYYYMM(occurred_at)
ORDER BY (
    source_service,
    toDate(occurred_at),
    event_id
)
TTL toDate(occurred_at) + INTERVAL 2 YEAR
SETTINGS index_granularity = 8192;

ALTER TABLE ${CLICKHOUSE_DB}.audit_events
    ADD INDEX IF NOT EXISTS idx_severity
    severity TYPE set(16)
    GRANULARITY 1;

ALTER TABLE ${CLICKHOUSE_DB}.audit_events
    ADD INDEX IF NOT EXISTS idx_event_type
    event_type TYPE set(128)
    GRANULARITY 1;

ALTER TABLE ${CLICKHOUSE_DB}.audit_events
    ADD INDEX IF NOT EXISTS idx_trace_id
    trace_id TYPE bloom_filter
    GRANULARITY 1;

ALTER TABLE ${CLICKHOUSE_DB}.audit_events
    ADD INDEX IF NOT EXISTS idx_occurred_at
    occurred_at TYPE minmax
    GRANULARITY 1;

ALTER TABLE ${CLICKHOUSE_DB}.audit_events
    ADD INDEX IF NOT EXISTS idx_actor_id
    actor_id TYPE bloom_filter
    GRANULARITY 2;
"

echo ">>> [ClickHouse init] Done."