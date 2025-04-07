import pytest
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas.contacts import ContactCreate, ContactUpdate
from src.repository.contacts import (
    create_contact, 
    get_contact, 
    get_contacts, 
    update_contact, 
    delete_contact, 
    get_upcoming_birthdays
)


# Helper class for mocking query results
class MockScalars:
    def __init__(self, items):
        self.items = items
    
    def all(self):
        return self.items


# Helper class for mocking execute results
class MockExecuteResult:
    def __init__(self, scalar_result=None, scalars_result=None):
        self.scalar_result = scalar_result
        self.scalars_result = scalars_result
    
    def scalar_one_or_none(self):
        return self.scalar_result
    
    def scalars(self):
        return self.scalars_result


class TestContactsRepository:
    """Tests for contacts repository"""

    @pytest.mark.asyncio
    async def test_create_contact(self):
        """Test for contact creation"""
        # Create test data
        contact_data = ContactCreate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            birthday=date(1990, 1, 1),
            additional_data="Test contact"
        )
        
        # Mock DB session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Call the tested function
        result = await create_contact(contact_data, mock_db, user_id=1)
        
        # Check results
        assert result is not None
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.email == "john.doe@example.com"
        assert result.phone == "+1234567890"
        assert result.user_id == 1
        
        # Check that appropriate session methods were called
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_contact_exists(self):
        """Test for retrieving an existing contact"""
        # Create a model contact
        mock_contact = Contact(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            birthday=datetime(1990, 1, 1),
            user_id=1
        )
        
        # Use patch for select function
        with patch('sqlalchemy.future.select') as mock_select:
            # Configure mock for result.scalar_one_or_none
            mock_execute_result = MagicMock()
            mock_execute_result.scalar_one_or_none.return_value = mock_contact
            
            # Configure DB session to return mock_execute_result
            mock_db = AsyncMock(spec=AsyncSession)
            mock_db.execute.return_value = mock_execute_result
            
            # Call the tested function
            result = await get_contact(1, mock_db)
            
            # Check the result
            assert result is mock_contact
            assert result.id == 1
            assert result.first_name == "John"
            
            # Verify that execute was called
            mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_contact_not_exists(self):
        """Test for retrieving a non-existent contact"""
        # Use patch for select function
        with patch('sqlalchemy.future.select') as mock_select:
            # Configure mock for result.scalar_one_or_none
            mock_execute_result = MagicMock()
            mock_execute_result.scalar_one_or_none.return_value = None
            
            # Configure DB session to return mock_execute_result
            mock_db = AsyncMock(spec=AsyncSession)
            mock_db.execute.return_value = mock_execute_result
            
            # Call the tested function
            result = await get_contact(999, mock_db)
            
            # Check the result
            assert result is None
            
            # Verify that execute was called
            mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_contacts_without_search(self):
        """Test for retrieving contacts list without search query"""
        # Create a mock list of contacts
        mock_contacts = [
            Contact(
                id=1,
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                phone="+1234567890",
                birthday=datetime(1990, 1, 1),
                user_id=1
            ),
            Contact(
                id=2,
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@example.com",
                phone="+0987654321",
                birthday=datetime(1992, 5, 15),
                user_id=1
            )
        ]
        
        # Create mock query result
        mock_scalars = MockScalars(mock_contacts)
        mock_result = MockExecuteResult(scalars_result=mock_scalars)
        
        # Mock DB session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        
        # Mock offset and limit execution to return the query itself
        with patch("sqlalchemy.future.select") as mock_select:
            mock_query = MagicMock()
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_select.return_value = mock_query
            
            # Call the tested function
            result = await get_contacts(skip=0, limit=10, search="", db=mock_db)
            
            # Check results
            assert result is not None
            assert len(result) == 2
            assert result[0].first_name == "John"
            assert result[1].first_name == "Jane"
            
            # Verify that the correct query was executed
            mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_contacts_with_search(self):
        """Test for retrieving contacts list with search query"""
        # Create a mock list of filtered contacts
        mock_filtered_contacts = [
            Contact(
                id=1,
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                phone="+1234567890",
                birthday=datetime(1990, 1, 1),
                user_id=1
            )
        ]
        
        # Create mock query result
        mock_scalars = MockScalars(mock_filtered_contacts)
        mock_result = MockExecuteResult(scalars_result=mock_scalars)
        
        # Mock DB session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        
        # Mock offset and limit execution to return the query itself
        with patch("sqlalchemy.future.select") as mock_select:
            mock_query = MagicMock()
            mock_query.filter.return_value = mock_query
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_select.return_value = mock_query
            
            # Call the tested function with search query
            result = await get_contacts(skip=0, limit=10, search="John", db=mock_db)
            
            # Check results
            assert result is not None
            assert len(result) == 1
            assert result[0].first_name == "John"
            
            # Verify that the correct query was executed
            mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_contact_exists(self):
        """Test for updating an existing contact"""
        # Create a mock existing contact
        mock_contact = Contact(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            birthday=datetime(1990, 1, 1),
            user_id=1
        )
        
        # Create update data
        update_data = ContactUpdate(
            first_name="John Updated",
            last_name="Doe Updated",
            email="john.updated@example.com",
            phone="+1234567890",
            birthday=date(1990, 1, 1),
            additional_data="Updated contact"
        )
        
        # Mock get_contact function to return our mock contact
        with patch("src.repository.contacts.get_contact", new=AsyncMock(return_value=mock_contact)):
            # Mock DB session
            mock_db = AsyncMock(spec=AsyncSession)
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()
            
            # Call the tested function
            result = await update_contact(contact_id=1, contact=update_data, db=mock_db)
            
            # Check results
            assert result is not None
            assert result.first_name == "John Updated"
            assert result.last_name == "Doe Updated"
            assert result.email == "john.updated@example.com"
            
            # Verify that appropriate session methods were called
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_contact_not_exists(self):
        """Test for updating a non-existent contact"""
        # Create update data
        update_data = ContactUpdate(
            first_name="John Updated",
            last_name="Doe Updated",
            email="john.updated@example.com",
            phone="+1234567890",
            birthday=date(1990, 1, 1),
            additional_data="Updated contact"
        )
        
        # Mock get_contact function to return None (contact not found)
        with patch("src.repository.contacts.get_contact", new=AsyncMock(return_value=None)):
            # Mock DB session
            mock_db = AsyncMock(spec=AsyncSession)
            
            # Call the tested function
            result = await update_contact(contact_id=999, contact=update_data, db=mock_db)
            
            # Check results
            assert result is None
            
            # Verify that commit and refresh methods were not called
            mock_db.commit.assert_not_called()
            mock_db.refresh.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_contact_exists(self):
        """Test for deleting an existing contact"""
        # Create a mock existing contact
        mock_contact = Contact(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            birthday=datetime(1990, 1, 1),
            user_id=1
        )
        
        # Mock get_contact function to return our mock contact
        with patch("src.repository.contacts.get_contact", new=AsyncMock(return_value=mock_contact)):
            # Mock DB session
            mock_db = AsyncMock(spec=AsyncSession)
            mock_db.delete = AsyncMock()
            mock_db.commit = AsyncMock()
            
            # Call the tested function
            result = await delete_contact(contact_id=1, db=mock_db)
            
            # Check results
            assert result is not None
            assert result.id == 1
            assert result.first_name == "John"
            
            # Verify that appropriate session methods were called
            mock_db.delete.assert_called_once_with(mock_contact)
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_contact_not_exists(self):
        """Test for deleting a non-existent contact"""
        # Mock get_contact function to return None (contact not found)
        with patch("src.repository.contacts.get_contact", new=AsyncMock(return_value=None)):
            # Mock DB session
            mock_db = AsyncMock(spec=AsyncSession)
            
            # Call the tested function
            result = await delete_contact(contact_id=999, db=mock_db)
            
            # Check results
            assert result is None
            
            # Verify that delete and commit methods were not called
            mock_db.delete.assert_not_called()
            mock_db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_upcoming_birthdays(self):
        """Test for retrieving list of upcoming birthdays"""
        # Fix current date for test
        today = date(2023, 5, 15)
        next_week = today + timedelta(days=7)
        
        # Create a mock list of contacts with upcoming birthdays
        mock_birthday_contacts = [
            Contact(
                id=1,
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                phone="+1234567890",
                birthday=datetime(1990, 5, 16),  # birthday on the next day
                user_id=1
            ),
            Contact(
                id=2,
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@example.com",
                phone="+0987654321",
                birthday=datetime(1992, 5, 20),  # birthday in 5 days
                user_id=1
            )
        ]
        
        # Create mock query result
        mock_scalars = MockScalars(mock_birthday_contacts)
        mock_result = MockExecuteResult(scalars_result=mock_scalars)
        
        # Mock DB session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        
        # Mock date.today function to return fixed date
        with patch("src.repository.contacts.date") as mock_date:
            mock_date.today.return_value = today
            
            # Call the tested function
            result = await get_upcoming_birthdays(db=mock_db)
            
            # Check results
            assert result is not None
            assert len(result) == 2
            assert result[0].first_name == "John"
            assert result[1].first_name == "Jane"
            
            # Verify that the correct query was executed
            mock_db.execute.assert_called_once() 