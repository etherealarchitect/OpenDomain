import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.api_key import ApiKey


class ApiKeyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _hash_key(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode()).hexdigest()

    async def create_key(self, user_id: uuid.UUID, data) -> dict:
        raw_key = f"od_{secrets.token_urlsafe(48)}"
        key_hash = self._hash_key(raw_key)
        prefix = raw_key[:8]

        expires_at = None
        if data.expires_in_days:
            expires_at = datetime.now(UTC) + timedelta(days=data.expires_in_days)

        api_key = ApiKey(
            user_id=user_id,
            name=data.name,
            key_hash=key_hash,
            prefix=prefix,
            scopes=",".join(data.scopes) if data.scopes else None,
            expires_at=expires_at,
        )
        self.db.add(api_key)
        await self.db.flush()
        await self.db.refresh(api_key)

        return {
            "id": str(api_key.id),
            "name": api_key.name,
            "key": raw_key,
            "prefix": prefix,
            "scopes": api_key.scopes,
            "expires_at": api_key.expires_at,
            "created_at": api_key.created_at,
        }

    async def list_keys(self, user_id: uuid.UUID) -> list[ApiKey]:
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.user_id == user_id).order_by(ApiKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def revoke_key(self, key_id: uuid.UUID, user_id: uuid.UUID):
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user_id)
        )
        api_key = result.scalar_one_or_none()
        if not api_key:
            raise ValueError("API key not found")
        api_key.active = False
        await self.db.flush()

    async def validate_key(self, raw_key: str) -> uuid.UUID | None:
        key_hash = self._hash_key(raw_key)
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.active.is_(True))
        )
        api_key = result.scalar_one_or_none()
        if not api_key:
            return None
        if api_key.expires_at and api_key.expires_at < datetime.now(UTC):
            api_key.active = False
            await self.db.flush()
            return None
        api_key.last_used = datetime.now(UTC)
        await self.db.flush()
        return api_key.user_id
