"""Verify the local storage stack. Run from the repository root."""
import subprocess


def compose(*args, stdin=None):
    result = subprocess.run(
        ["docker", "compose", *args], input=stdin, text=True,
        capture_output=True, check=True,
    )
    return result.stdout.strip()


def clickhouse(sql):
    return compose(
        "exec", "-T", "programmisto_clickhouse", "bash", "-ec",
        'exec clickhouse-client --user "$CLICKHOUSE_USER" '
        '--password "$CLICKHOUSE_PASSWORD" --database "$CLICKHOUSE_DB" --multiquery',
        stdin=sql,
    )


def redis(*args):
    return compose(
        "exec", "-T", "programmisto_redis", "sh", "-ec",
        'export REDISCLI_AUTH="$REDIS_PASSWORD"; exec redis-cli "$@"', "sh", *args,
    )


compose("config", "--quiet")
compose("up", "-d", "--wait", "--wait-timeout", "180")
compose("exec", "-T", "programmisto_clickhouse", "bash", "-n",
        "/docker-entrypoint-initdb.d/init-databases.sh")
# Explicit re-run proves that table/index creation is idempotent.
compose("exec", "-T", "programmisto_clickhouse", "bash",
        "/docker-entrypoint-initdb.d/init-databases.sh")
assert clickhouse("SELECT count() FROM system.tables WHERE database = currentDatabase() "
                  "AND name IN ('telemetry', 'device_events', 'audit_events')") == "3"
clickhouse("CREATE TABLE IF NOT EXISTS _infrastructure_smoke AS telemetry ENGINE=MergeTree ORDER BY tuple(); "
           "TRUNCATE TABLE _infrastructure_smoke; "
           "INSERT INTO _infrastructure_smoke "
           "(organization_id, building_id, device_id, metric, event_id, measured_at, value) "
           "SELECT generateUUIDv4(), generateUUIDv4(), generateUUIDv4(), 'temperature', "
           "generateUUIDv4(), now64(3), 42;")
assert redis("PING") == "PONG"
assert redis("SET", "ujin:smoke:infrastructure", "42", "EX", "300") == "OK"
compose("restart", "programmisto_redis", "programmisto_clickhouse")
compose("up", "-d", "--wait", "--wait-timeout", "180")
assert clickhouse("SELECT value FROM _infrastructure_smoke") == "42"
assert redis("GET", "ujin:smoke:infrastructure") == "42"
clickhouse("DROP TABLE _infrastructure_smoke SYNC")
assert redis("DEL", "ujin:smoke:infrastructure") == "1"
print("PASS: telemetry schema, repeat initialization, read/write and persistence after restart")
print(compose("ps"))
