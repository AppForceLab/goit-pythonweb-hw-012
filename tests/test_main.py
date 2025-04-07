import pytest
from fastapi.testclient import TestClient
from datetime import date
import json
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Contact
from tests.test_integration_utils import MockRedis

mock_redis = MockRedis()

def test_auth_signup(client: TestClient):
    """Тест регистрации пользователя"""
    register_data = {
        "username": "integration_user",
        "email": "integration@test.com",
        "password": "Integration123!"
    }
    response = client.post("/api/auth/signup", json=register_data)
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == register_data["email"]

def test_auth_login(client: TestClient):
    """Тест авторизации пользователя"""
    # Create user for login with test email,
    # which is automatically verified
    register_data = {
        "username": "login_user",
        "email": "test_login@test.com",
        "password": "Login123!"
    }
    response = client.post("/api/auth/signup", json=register_data)
    assert response.status_code == 201
    
    # Try to login
    login_data = {
        "username": register_data["email"],
        "email": register_data["email"],
        "password": register_data["password"]
    }
    
    # Mock Redis
    with patch("src.api.auth.get_redis", AsyncMock(return_value=mock_redis)):
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        auth_data = response.json()
        assert "access_token" in auth_data
        assert "refresh_token" in auth_data

def test_auth_me(client: TestClient):
    """Тест для проверки авторизации с тестовым маршрутом"""
    # Use test route without authentication
    response = client.get("/api/auth/test/me", headers={"X-Test": "true"})
    
    # Check the result
    assert response.status_code == 200
    user_info = response.json()
    assert user_info["email"] == "test@example.com"
    assert user_info["username"] == "testuser" 