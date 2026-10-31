"""Local audit adapter; optional HTTP endpoint is configured as a complete URL."""

from datetime import datetime, timezone
import json
import logging
from uuid import uuid4

import httpx

logger = logging.getLogger("auth.audit")


def redact_context(value):
    if isinstance(value, dict):
        return {
            key: "[redacted]"
            if any(
                word in str(key).lower()
                for word in ("password", "token", "secret", "authorization", "cookie")
            )
            else redact_context(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_context(item) for item in value]
    return value


class AuditClient:
    def __init__(self, audit_url=None, source_service="auth"):
        self.audit_url = audit_url
        self.source_service = source_service
        self.client = httpx.AsyncClient(timeout=3) if audit_url else None

    async def send(
        self,
        *,
        event_type,
        actor_id=None,
        actor_type=None,
        entity_type=None,
        entity_id=None,
        trace_id=None,
        severity="info",
        context=None,
    ):
        event = dict(
            event_id=str(uuid4()),
            source_service=self.source_service,
            event_type=event_type,
            actor_id=actor_id,
            actor_type=actor_type,
            entity_type=entity_type,
            entity_id=entity_id,
            trace_id=trace_id,
            severity=severity,
            context=redact_context(context or {}),
            occurred_at=datetime.now(timezone.utc).isoformat(),
        )
        # Local logging is an explicit sink, not confirmation of remote storage.
        if self.client is None:
            logger.info("AUDIT %s", json.dumps(event, ensure_ascii=False))
            return
        response = await self.client.post(self.audit_url, json=event)
        response.raise_for_status()

    async def aclose(self):
        if self.client is not None:
            await self.client.aclose()
