import json
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_db
from src.database.models import User
from src.services.redis_client import get_redis

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: AsyncSession = Depends(get_db)) -> User:
    """Validate JWT token and return the current user.
    
    This function validates the JWT token from the Authorization header,
    retrieves user information from Redis cache or database,
    and returns the User object for the authenticated user.
    
    Args:
        token: JWT token from Authorization header
        db: Database session dependency
        
    Returns:
        User: Authenticated user object
        
    Raises:
        HTTPException: With 401 status code if token is invalid or user not found
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_email = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # For test environment we don't use Redis
    if user_email and user_email.startswith("test_"):
        result = await db.execute(select(User).where(User.email == user_email))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user

    redis = await get_redis()
    cached_user = await redis.get(f"user:{user_email}")
    if cached_user:
        user_data = json.loads(cached_user)
        return User(**user_data)

    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    await redis.set(f"user:{user_email}", json.dumps({
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "avatar": user.avatar,
        "role": user.role
    }))
    return user
