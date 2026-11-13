import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from .models import Subscription, User
from .security import decode_token
from .utils import utcnow

bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    err = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing token")
    if not creds:
        raise err
    try:
        uid = uuid.UUID(decode_token(creds.credentials)["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise err
    user = await db.get(User, uid)
    if not user or not user.is_active:
        raise err
    return user


async def get_subscription(db: AsyncSession, user_id) -> Subscription | None:
    sub = await db.get(Subscription, user_id)
    return sub if sub and sub.expires_at > utcnow() else None


async def is_premium(db: AsyncSession, user_id) -> bool:
    return (await get_subscription(db, user_id)) is not None


async def require_premium(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> User:
    if not await is_premium(db, user.id):
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, "Kutana Black subscription required")
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin only")
    return user
