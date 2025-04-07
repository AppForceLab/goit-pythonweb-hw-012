import pytest
from unittest.mock import patch, AsyncMock
import json

from src.services.redis_client import get_redis, set_user_cache, get_user_cache, delete_user_cache

class TestRedisClient:
    """Tests for Redis client operations"""
    
    @pytest.mark.asyncio
    async def test_get_redis(self):
        """Test getting Redis client"""
        # Mock redis connection
        with patch("src.services.redis_client.redis.Redis") as mock_redis_class:
            mock_redis_instance = AsyncMock()
            mock_redis_class.from_url.return_value = mock_redis_instance
            
            # Call the function
            result = await get_redis()
            
            # Check that from_url was called with correct parameters
            mock_redis_class.from_url.assert_called_once()
            
            # Since we're testing a global variable, reset it after the test
            import src.services.redis_client
            src.services.redis_client.redis_client = None
    
    @pytest.mark.asyncio
    async def test_set_user_cache(self):
        """Test setting user data in cache"""
        # Test data
        user_id = 1
        user_data = {
            "id": user_id,
            "email": "test@example.com",
            "username": "testuser"
        }
        
        # Mock redis client
        with patch("src.services.redis_client.get_redis") as mock_get_redis:
            # Create mock for Redis
            mock_redis = AsyncMock()
            mock_get_redis.return_value = mock_redis
            
            # Call the function
            await set_user_cache(user_id, user_data)
            
            # Check that setex method was called with correct arguments
            mock_redis.setex.assert_called_once_with(
                f"user:{user_id}",
                3600,  # cache lifetime (1 hour)
                json.dumps(user_data)
            )
    
    @pytest.mark.asyncio
    async def test_get_user_cache_hit(self):
        """Test getting user data from cache (data exists)"""
        # Test data
        user_id = 1
        user_data = {
            "id": user_id,
            "email": "test@example.com",
            "username": "testuser"
        }
        
        # Mock redis client
        with patch("src.services.redis_client.get_redis") as mock_get_redis:
            # Create mock for Redis
            mock_redis = AsyncMock()
            mock_redis.get.return_value = json.dumps(user_data)
            mock_get_redis.return_value = mock_redis
            
            # Call the function
            result = await get_user_cache(user_id)
            
            # Check that result matches expected
            assert result == user_data
            mock_redis.get.assert_called_once_with(f"user:{user_id}")
    
    @pytest.mark.asyncio
    async def test_get_user_cache_miss(self):
        """Test getting user data from cache (no data)"""
        # Test data
        user_id = 1
        
        # Mock redis client
        with patch("src.services.redis_client.get_redis") as mock_get_redis:
            # Create mock for Redis
            mock_redis = AsyncMock()
            mock_redis.get.return_value = None  # Nothing in cache
            mock_get_redis.return_value = mock_redis
            
            # Call the function
            result = await get_user_cache(user_id)
            
            # Check that result is None
            assert result is None
            mock_redis.get.assert_called_once_with(f"user:{user_id}")
    
    @pytest.mark.asyncio
    async def test_delete_user_cache(self):
        """Test deleting user data from cache"""
        # Test data
        user_id = 1
        
        # Mock redis client
        with patch("src.services.redis_client.get_redis") as mock_get_redis:
            # Create mock for Redis
            mock_redis = AsyncMock()
            mock_get_redis.return_value = mock_redis
            
            # Call the function
            await delete_user_cache(user_id)
            
            # Check that delete method was called with correct arguments
            mock_redis.delete.assert_called_once_with(f"user:{user_id}") 