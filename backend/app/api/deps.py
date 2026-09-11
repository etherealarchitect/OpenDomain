import uuid
from typing import Annotated

from backend.app.core.database import get_db
from backend.app.core.security import decode_access_token
from backend.app.models.user import User
from backend.app.services.auth_service import AuthService
from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

security = HTTPBearer(auto_error=False)
SESSION_COOKIE = "opendomain_session"


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE),
) -> User:
    """Require a complete account via an opaque cookie session.

    A temporary bearer-token fallback maintains CLI compatibility during the
    migration, but browser clients exclusively use HttpOnly session cookies.
    """
    if session_token:
        user = await AuthService(db).get_session_user(session_token)
        if user:
            return user

    if credentials:
        try:
            payload = decode_access_token(credentials.credentials)
            user_id = payload.get("sub")
            if user_id is not None:
                user = await db.scalar(select(User).where(User.id == uuid.UUID(user_id)))
                if user and user.is_active and user.is_verified and user.two_factor_enabled:
                    return user
        except (JWTError, ValueError):
            pass

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in required")


CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
