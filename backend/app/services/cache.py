import hashlib
import json
import logging
from redis.asyncio import from_url
from app.core.config import settings

logger = logging.getLogger(__name__)

class AnswerCache:
    def __init__(self) -> None:
        self.client = from_url(settings.redis_url, decode_responses=True)
        self.ttl_seconds = 3600

    def key(self, repo: str, question: str, top_k: int) -> str:
        digest = hashlib.sha256(f"{repo}:{top_k}:{question.strip().lower()}".encode("utf-8")).hexdigest()
        return f"atlas:answer:{digest}"

    async def get(self, repo: str, question: str, top_k: int) -> dict | None:
        try:
            raw = await self.client.get(self.key(repo, question, top_k))
            return json.loads(raw) if raw else None
        except Exception as exc:
            logger.warning("cache_get_failed", exc_info=exc)
            return None

    async def set(self, repo: str, question: str, top_k: int, value: dict) -> None:
        try:
            await self.client.setex(self.key(repo, question, top_k), self.ttl_seconds, json.dumps(value))
        except Exception as exc:
            logger.warning("cache_set_failed", exc_info=exc)
