import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.auth.hashing import hash_password, verify_password


def test_hashing_functions():
    """
    Тест функций хеширования паролей
    """
    # Тестовые данные
    password = "secure_password"
    
    # Хешируем пароль
    hashed = hash_password(password)
    
    # Проверяем, что хеш не равен оригинальному паролю
    assert hashed != password
    
    # Проверяем, что верификация работает корректно
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed) 