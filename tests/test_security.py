import pytest
from unittest.mock import patch

from src.services.security import get_password_hash, verify_password

class TestSecurity:
    """Тесты для функций безопасности"""
    
    def test_get_password_hash(self):
        """Тест хеширования пароля"""
        # Check that hash is not equal to original password
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert hashed != password
        
        # Check hash format - should start with $2b$ (bcrypt)
        assert hashed.startswith("$2b$")
        
        # Check that hash is long enough
        assert len(hashed) > 50
    
    def test_verify_password(self):
        """Тест проверки пароля"""
        # Correct password
        assert verify_password("testpassword123", get_password_hash("testpassword123"))
        
        # Incorrect password
        assert not verify_password("wrongpassword", get_password_hash("testpassword123"))
        
        # Empty password
        assert not verify_password("", get_password_hash("testpassword123"))
    
    def test_verify_password_with_mocked_bcrypt(self):
        """Тест проверки пароля с моком bcrypt"""
        # Mock functions from bcrypt
        with patch("src.services.security.pwd_context.verify") as mock_verify:
            mock_verify.return_value = True
            
            # Check validation through mock
            assert verify_password("testpassword123", "hashed_password")
            
            # Check that mock was called with correct parameters
            mock_verify.assert_called_once_with("testpassword123", "hashed_password")
            
            # Change mock behavior
            mock_verify.return_value = False
            assert not verify_password("wrongpassword", "hashed_password") 