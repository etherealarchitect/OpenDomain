"""Small Redis-backed, fixed-window rate limiter for authentication endpoints."""

from __future__ import annotations

import hashlib
import time

from backend.app.core.config import settings
from redis.asyncio import Redis
from redis.exceptions import RedisError


class RateLimitUnavailableError(RuntimeError):
    """Raised when production authentication throttling cannot be enforced."""


class AuthRateLimiter:
    """Use Redis in production and a bounded process-local fallback in development."""

    def __init__(self) -> None:
        self._client: Redis | None = None
        self._fallback: dict[str, tuple[int, float]] = {}

    def _redis(self) -> Redis:
        if self._client is None:
            self._client = Redis.from_url(settings.redis_url, decode_responses=True)
        return self._client

    @staticmethod
    def _key(scope: str, identifier: str) -> str:
        digest = hashlib.sha256(identifier.encode()).hexdigest()
        return f"opendomain:auth-rate-limit:{scope}:{digest}"

    async def check(self, scope: str, identifier: str, limit: int, window_seconds: int) -> None:
        key = self._key(scope, identifier)
        try:
            client = self._redis()
            count = await client.incr(key)
            if count == 1:
                await client.expire(key, window_seconds)
            if count > limit:
                raise ValueError("Too many attempts. Please wait and try again.")
            return
        except ValueError:
            raise
        except RedisError as exc:
            if settings.is_production:
                raise RateLimitUnavailableError(
                    "Authentication is temporarily unavailable"
                ) from exc
            self._check_fallback(key, limit, window_seconds)

    def _check_fallback(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.monotonic()
        count, expires_at = self._fallback.get(key, (0, now + window_seconds))
        if expires_at <= now:
            count, expires_at = 0, now + window_seconds
        count += 1
        self._fallback[key] = (count, expires_at)
        if len(self._fallback) > 5_000:
            self._fallback = {k: value for k, value in self._fallback.items() if value[1] > now}
        if count > limit:
            raise ValueError("Too many attempts. Please wait and try again.")


rate_limiter = AuthRateLimiter()
