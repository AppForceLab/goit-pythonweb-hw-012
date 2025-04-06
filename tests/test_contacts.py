import uuid
import pytest
import pytest_asyncio
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas.contacts import ContactCreate, ContactUpdate
from src.repository.contacts import (
    create_contact,
    get_contact,
    get_contacts,
    update_contact,
    delete_contact,
)


@pytest_asyncio.fixture
async def user(async_session: AsyncSession) -> User:
    unique_username = f"tester-{uuid.uuid4()}"
    new_user = User(
        username=unique_username,
        email=f"{unique_username}@example.com",
        password="hashed"
    )
    async_session.add(new_user)
    await async_session.commit()
    await async_session.refresh(new_user)
    return new_user


@pytest.mark.asyncio
async def test_create_contact(async_session: AsyncSession, user: User):
    contact_data = ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="1234567890",
        birthday=date.today(),
        additional_data="Test contact"
    )

    created = await create_contact(contact_data, async_session, user_id=user.id)

    assert created.id is not None
    assert created.first_name == "John"
    assert created.user_id == user.id


@pytest.mark.asyncio
async def test_get_contact(async_session: AsyncSession, user: User):
    contact_data = ContactCreate(
        first_name="Alice",
        last_name="Wonder",
        email="alice@example.com",
        phone="555-1234",
        birthday=date.today(),
        additional_data="Example contact"
    )

    created = await create_contact(contact_data, async_session, user_id=user.id)
    retrieved = await get_contact(created.id, async_session)

    assert retrieved is not None
    assert retrieved.email == "alice@example.com"


@pytest.mark.asyncio
async def test_get_contacts(async_session: AsyncSession, user: User):
    await create_contact(ContactCreate(
        first_name="Searchable",
        last_name="Contact",
        email="search@example.com",
        phone="0000000",
        birthday=date.today(),
        additional_data="To be found"
    ), async_session, user_id=user.id)

    results = await get_contacts(skip=0, limit=10, search="Search", db=async_session)
    assert any("Searchable" in contact.first_name for contact in results)


@pytest.mark.asyncio
async def test_update_contact(async_session: AsyncSession, user: User):
    created = await create_contact(ContactCreate(
        first_name="OldName",
        last_name="OldLast",
        email="old@example.com",
        phone="123",
        birthday=date.today(),
        additional_data="Old"
    ), async_session, user_id=user.id)

    updated = await update_contact(created.id, ContactUpdate(
        first_name="NewName",
        last_name="NewLast",
        email="new@example.com",
        phone="456",
        birthday=date.today(),
        additional_data="Updated"
    ), async_session)

    assert updated.first_name == "NewName"
    assert updated.email == "new@example.com"


@pytest.mark.asyncio
async def test_delete_contact(async_session: AsyncSession, user: User):
    created = await create_contact(ContactCreate(
        first_name="DeleteMe",
        last_name="User",
        email="delete@example.com",
        phone="999",
        birthday=date.today(),
        additional_data="Remove me"
    ), async_session, user_id=user.id)

    deleted = await delete_contact(created.id, async_session)
    assert deleted is not None

    should_be_none = await get_contact(created.id, async_session)
    assert should_be_none is None
