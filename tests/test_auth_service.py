import json
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.services.auth import get_current_user
from src.database.models import User
from src.conf.config import settings


class MockResult:
    """Mock class for database results"""
    def __init__(self, value):
        self.value = value
    
    def scalar_one_or_none(self):
        """Non-async version to work with mocked services"""
        return self.value


class TestAuthService:
    """Tests for authentication service"""
    
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        """Test getting current user with valid token"""
        # Mock jwt.decode to return payload with sub
        with patch("src.services.auth.jwt.decode") as mock_decode:
            # Return payload with user email
            mock_decode.return_value = {"sub": "test@example.com"}
            
            # Create user to return from DB
            test_user = User(
                id=1,
                email="test@example.com",
                username="testuser",
                password="hashedpass",
                confirmed=True,
                avatar=None,
                role="user"
            )
            
            # Setup Redis mock
            with patch("src.services.auth.get_redis") as mock_get_redis:
                mock_redis = AsyncMock()
                mock_redis.get.return_value = None  # No cache
                mock_get_redis.set = AsyncMock()  # Mock for set method
                mock_get_redis.return_value = mock_redis
                
                # Mock DB session and execution
                mock_session = AsyncMock()
                
                # Mock the scalar_one_or_none to return a proper value, not a coroutine
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = test_user
                mock_session.execute.return_value = mock_result
                
                # Mock the select function
                with patch("src.services.auth.select") as mock_select:
                    # Call tested function
                    user = await get_current_user("test_token", mock_session)
                    
                    # Check result
                    assert user is not None
                    assert user.email == "test@example.com"
                    
                    # Check that jwt.decode was called with correct parameters
                    mock_decode.assert_called_once_with("test_token", settings.secret_key, algorithms=[settings.algorithm])
    
    @pytest.mark.asyncio
    async def test_get_current_user_from_cache(self):
        """Test getting current user from cache"""
        # Mock jwt.decode to return payload with sub
        with patch("src.services.auth.jwt.decode") as mock_decode:
            # Return payload with user email
            mock_decode.return_value = {"sub": "test@example.com"}
            
            # Mock Redis
            with patch("src.services.auth.get_redis") as mock_get_redis:
                # Setup Redis mock with data in cache
                mock_redis = AsyncMock()
                cached_user = {
                    "id": 1,
                    "email": "test@example.com",
                    "username": "testuser",
                    "avatar": None,
                    "role": "user",
                    "password": "hashedpass"
                }
                mock_redis.get.return_value = json.dumps(cached_user)
                mock_get_redis.return_value = mock_redis
                
                # Create mock session
                mock_session = AsyncMock()
                
                # Call tested function
                user = await get_current_user("test_token", mock_session)
                
                # Check result
                assert user is not None
                assert user.email == "test@example.com"
                assert user.username == "testuser"
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token"""
        # Mock jwt.decode to simulate JWTError
        with patch("src.services.auth.jwt.decode") as mock_decode:
            # Simulate exception when decoding
            mock_decode.side_effect = JWTError("Invalid token")
            
            # Create mock session
            mock_session = AsyncMock()
            
            # Check that exception is raised
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("invalid_token", mock_session)
            
            # Check exception parameters
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Invalid token"
    
    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self):
        """Test getting current user when user is not found"""
        # Mock jwt.decode to return payload with sub
        with patch("src.services.auth.jwt.decode") as mock_decode:
            # Return payload with user email
            mock_decode.return_value = {"sub": "nonexistent@example.com"}
            
            # Setup Redis mock
            with patch("src.services.auth.get_redis") as mock_get_redis:
                mock_redis = AsyncMock()
                mock_redis.get.return_value = None  # No cache
                mock_get_redis.return_value = mock_redis
            
                # Mock DB to return None
                mock_session = AsyncMock()
                
                # Mock the scalar_one_or_none to return None
                mock_result = MagicMock()
                mock_result.scalar_one_or_none.return_value = None
                mock_session.execute.return_value = mock_result
                
                # Mock the select function
                with patch("src.services.auth.select") as mock_select:
                    # Check that exception is raised
                    with pytest.raises(HTTPException) as exc_info:
                        await get_current_user("test_token", mock_session)
                    
                    # Check exception parameters
                    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                    assert exc_info.value.detail == "User not found"
    
    @pytest.mark.asyncio
    async def test_get_current_user_test_env(self):
        """Test getting current user in test environment"""
        # Mock jwt.decode to return payload with test email
        with patch("src.services.auth.jwt.decode") as mock_decode:
            # Return payload with test email user
            mock_decode.return_value = {"sub": "test_user@example.com"}
            
            # Create test user for mock
            test_user = User(
                id=1,
                email="test_user@example.com",
                username="test_user",
                password="hashedpass",
                confirmed=True,
                avatar=None,
                role="user"
            )
            
            # Mock DB session and execution
            mock_session = AsyncMock()
            
            # Mock the scalar_one_or_none to return a proper value, not a coroutine
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = test_user
            mock_session.execute.return_value = mock_result
            
            # Mock the select function
            with patch("src.services.auth.select") as mock_select:
                # Call tested function
                user = await get_current_user("test_token", mock_session)
                
                # Check result
                assert user is not None
                assert user.email == "test_user@example.com" 