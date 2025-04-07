import json
from typing import Optional
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from fastapi.testclient import TestClient

from src.conf.config import settings
from src.database.models import User
from src.services.auth import oauth2_scheme
from src.services.redis_client import get_redis

# Mock Redis client for tests
class MockRedis:
    """Mock class for Redis client"""
    def __init__(self):
        self.storage = {}

    async def get(self, key):
        """Get value from mock storage"""
        return self.storage.get(key)

    async def set(self, key, value, ex=None):
        """Set value in mock storage"""
        self.storage[key] = value

    async def delete(self, key):
        """Delete value from mock storage"""
        if key in self.storage:
            del self.storage[key]
    
    async def setex(self, key, expire, value):
        """Set value with expiration time"""
        self.storage[key] = value

mock_redis = MockRedis()

# Override get_redis function for tests
@pytest.fixture(scope="session", autouse=True)
def override_get_redis():
    """Override get_redis function for use in tests"""
    async def mock_get_redis():
        return mock_redis

    with patch("src.services.redis_client.get_redis", mock_get_redis):
        with patch("src.services.auth.get_redis", mock_get_redis):
            with patch("src.api.auth.get_redis", mock_get_redis):
                yield


# Override get_current_user function for tests
async def mock_get_current_user(token: str = Depends(oauth2_scheme),
                           db: AsyncSession = Depends(),
                           request: Request = None) -> User:
    """
    Function to get current user for tests,
    does not use Redis for caching
    """
    # Check X-Test header
    if request and request.headers.get("X-Test") == "true":
        # Return test user without token validation
        return User(
            id=1,
            username="testuser",
            email="test@example.com",
            password="hashed_password",
            confirmed=True,
            role="user"
        )
        
    # Normal token validation
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_email = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


async def mock_read_me(request: Request):
    """Test function to get user information without JWT token"""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "role": "user",
        "avatar": None,
        "created_at": "2023-01-01T00:00:00", 
        "confirmed": True
    }

def test_utils(app):
    """Test utilities for integration tests"""
    test_headers = {"X-Test": "true"}
    test_http_client = TestClient(app)
    
    # Check X-Test header functionality
    if test_headers["X-Test"] == "true":
        assert test_http_client is not None
        return test_http_client 