import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class StateRepository:
    def __init__(self):
        self.redis: redis.Redis | None = None

    async def connect(self):
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)
        await self.redis.ping()
        logger.info("Connected to Redis")

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def update_state(self, device_id: str, state_data: Dict[str, Any], quality: str = "good"):
        if not self.redis:
            return
            
        key = f"iot:device:{device_id}:state"
        data = {
            "state": json.dumps(state_data),
            "received_at": datetime.now(timezone.utc).isoformat(),
            "quality": quality
        }
        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.hset(key, mapping=data)
            pipe.expire(key, 86400)
            await pipe.execute()

    async def get_state(self, device_id: str) -> Dict[str, Any]:
        if not self.redis:
            return {}
            
        key = f"iot:device:{device_id}:state"
        data = await self.redis.hgetall(key)
        if not data:
            return {}
            
        return {
            "signals": json.loads(data["state"]),
            "received_at": data["received_at"],
            "quality": data["quality"]
        }

state_repo = StateRepository()