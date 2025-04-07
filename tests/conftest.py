import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from collections.abc import AsyncGenerator
from unittest.mock import patch, AsyncMock
import uuid
import json
import asyncio
import time
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy import event
from sqlalchemy.exc import SQLAlchemyError

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.database.models import Base, User, Contact
from src.database.models import Base, User
from src.database.db import get_db
from src.conf.config import settings
from main import app as main_app
from src.services.auth import get_current_user
from tests.test_integration_utils import mock_get_current_user, mock_read_me
from src.api.auth import read_me as original_read_me
from src.services.redis_client import redis_client

# Use SQLite in-memory for tests
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

TestingSessionLocal = async_sessionmaker(
    engine_test, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False, 
    autoflush=False
)

# Mock function for sending emails
async def mock_send_email(*args, **kwargs):
    """Mock function to intercept email sending"""
    return True

@pytest.fixture(scope="session", autouse=True)
def override_email_sending():
    """Override email sending function for tests"""
    with patch("src.services.email.send_verification_email", mock_send_email):
        with patch("src.services.email.send_reset_password_email", mock_send_email):
            yield

@pytest.fixture(scope="session", autouse=True)
def override_settings_database_url():
    """Override database URL to use SQLite during tests"""
    with patch.object(settings.__class__, 'database_url', new=DATABASE_URL):
        yield

@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    """Prepare test database"""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Apply migrations?
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="module")
async def client() -> AsyncGenerator[TestClient, None]:
    """Return FastAPI TestClient for testing synchronous endpoints"""
    # Create app for testing
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Use override to replace read_me function
    with patch("src.api.auth.redis_client", redis_client):
        with patch("src.services.auth.redis_client", redis_client):
            with patch("src.api.auth.read_me", read_me_test):
                # Return test client
                with TestClient(app) as test_client:
                    yield test_client

# Fix function for mocking read_me during tests
async def read_me_test(request, db):
    """Test version of read_me function to always return test data"""
    test_header = request.headers.get("x-test")
    if test_header:
        # Return a fixed test user when X-Test header is present
        return {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com", 
            "avatar": None,
            "role": "user"
        }
    # Otherwise use the original function
    return await original_read_me(request, db)

@pytest.fixture(scope="module")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Return AsyncClient for testing asynchronous endpoints"""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Use override to replace read_me function
    with patch("src.api.auth.redis_client", redis_client):
        with patch("src.services.auth.redis_client", redis_client):
            with patch("src.api.auth.read_me", read_me_test):
                # Return async client
                async with AsyncClient(app=app, base_url="http://test") as test_client:
                    yield test_client

@pytest.fixture(scope="module")
async def async_session_maker():
    """Create tables in the test database"""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield TestingSessionLocal

@pytest.fixture
def app():
    """Returns application instance with overriden dependencies"""
    app = main_app
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[original_read_me] = mock_read_me
    return app

@pytest.fixture
def client(app):
    """Create FastAPI test client"""
    return TestClient(app)

@pytest_asyncio.fixture
async def test_user(async_session) -> User:
    """Create test user with unique email"""
    # Create hashed password
    from src.services.security import get_password_hash
    password_hash = get_password_hash("testpassword123")
    
    # Generate unique email and username for each test
    unique_id = uuid.uuid4()
    test_email = f"test_{unique_id}@example.com"
    test_username = f"TestUser_{unique_id}"
    
    # Create test user
    test_user = User(
        username=test_username,
        email=test_email,
        password=password_hash,
        confirmed=True
    )
    
    async_session.add(test_user)
    await async_session.commit()
    await async_session.refresh(test_user)
    
    return test_user

@pytest.fixture
def test_auth_header(client, test_user) -> dict:
    """Get test authorization header"""
    # Use synchronous request with TestClient
    response = client.post(
        "/api/auth/login",
        json={"username": test_user.email, "email": test_user.email, "password": "testpassword123"}
    )
    data = response.json()
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def contact_data():
    """Test data for contact creation"""
    from datetime import date
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "birthday": str(date(1990, 1, 15)),
        "additional_data": "Test contact"
    }

@pytest_asyncio.fixture
async def test_contact(async_session, test_user, contact_data):
    """Create test contact in database"""
    contact = Contact(
        **contact_data,
        user_id=test_user.id
    )
    async_session.add(contact)
    await async_session.commit()
    await async_session.refresh(contact)
    return contact

@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Async session fixture for database tests"""
    async with TestingSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        finally:
            await session.close()

async def override_get_db():
    """Override get_db dependency for tests"""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
