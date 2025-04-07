import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from src.auth.handlers import create_user, authenticate_user, get_current_user
from src.database.models import User


class TestAuthHandlers:
    """Тесты для обработчиков аутентификации"""

    @pytest.mark.asyncio
    async def test_create_user_success(self):
        """Тест успешного создания пользователя"""
        # Мокируем результат запроса, возвращающий None (email не существует)
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        
        # Создаем мок для execute метода с правильным возвратом result
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Вызываем тестируемую функцию
        with patch("src.auth.handlers.hash_password") as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            result = await create_user(
                username="testuser",
                email="test@example.com",
                password="password123",
                db=mock_db
            )
            
            # Проверяем результат
            assert result is not None
            assert result.username == "testuser"
            assert result.email == "test@example.com"
            assert result.password == "hashed_password"
            
            # Проверяем, что были вызваны соответствующие методы
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
            mock_hash.assert_called_once_with("password123")

    @pytest.mark.asyncio
    async def test_create_user_email_exists(self):
        """Тест создания пользователя с уже существующим email"""
        # Мокируем результат запроса, возвращающий существующего пользователя
        mock_user = User(
            id=1,
            email="existing@example.com",
            username="existinguser",
            password="hashed_password"
        )
        
        mock_result = MagicMock()
        mock_result.scalar.return_value = mock_user
        
        # Создаем мок для execute метода с правильным возвратом result
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        
        # Проверяем, что вызывается исключение
        with pytest.raises(HTTPException) as exc_info:
            await create_user(
                username="testuser",
                email="existing@example.com",
                password="password123",
                db=mock_db
            )
        
        # Проверяем параметры исключения
        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "Email already registered"

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self):
        """Тест успешной аутентификации пользователя"""
        # Мокируем результат запроса, возвращающий существующего пользователя
        mock_user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            password="hashed_password"
        )
        
        mock_result = MagicMock()
        mock_result.scalar.return_value = mock_user
        
        # Создаем мок для execute метода с правильным возвратом result
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        
        # Вызываем тестируемую функцию
        with patch("src.auth.handlers.verify_password") as mock_verify:
            mock_verify.return_value = True
            
            result = await authenticate_user(
                email="test@example.com",
                password="password123",
                db=mock_db
            )
            
            # Проверяем результат
            assert result is mock_user
            
            # Проверяем, что verify_password был вызван с правильными параметрами
            mock_verify.assert_called_once_with("password123", "hashed_password")

    @pytest.mark.asyncio
    async def test_authenticate_user_test_env(self):
        """Тест аутентификации тестового пользователя"""
        # Мокируем результат запроса, возвращающий тестового пользователя
        mock_test_user = User(
            id=999,
            email="test_user@example.com",
            username="test_user",
            password="some_password"  # Не важно, т.к. в тестовом режиме не проверяется
        )
        
        mock_result = MagicMock()
        mock_result.scalar.return_value = mock_test_user
        
        # Создаем мок для execute метода с правильным возвратом result
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        
        # Вызываем тестируемую функцию с тестовыми данными
        result = await authenticate_user(
            email="test_user@example.com",
            password="testpassword123",  # Специальный тестовый пароль
            db=mock_db
        )
        
        # Проверяем результат
        assert result is mock_test_user

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_credentials(self):
        """Тест аутентификации с неверными учетными данными"""
        # Мокируем результат запроса, возвращающий существующего пользователя
        mock_user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            password="hashed_password"
        )
        
        mock_result = MagicMock()
        mock_result.scalar.return_value = mock_user
        
        # Создаем мок для execute метода с правильным возвратом result
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        
        # Вызываем тестируемую функцию с неверным паролем
        with patch("src.auth.handlers.verify_password") as mock_verify:
            mock_verify.return_value = False  # Пароль не совпадает
            
            # Проверяем, что вызывается исключение
            with pytest.raises(HTTPException) as exc_info:
                await authenticate_user(
                    email="test@example.com",
                    password="wrong_password",
                    db=mock_db
                )
            
            # Проверяем параметры исключения
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self):
        """Тест аутентификации несуществующего пользователя"""
        # Мокируем результат запроса, возвращающий None (пользователь не найден)
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        
        # Создаем мок для execute метода с правильным возвратом result
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        
        # Проверяем, что вызывается исключение
        with pytest.raises(HTTPException) as exc_info:
            await authenticate_user(
                email="nonexistent@example.com",
                password="password123",
                db=mock_db
            )
        
        # Проверяем параметры исключения
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """Тест успешного получения текущего пользователя"""
        # Мокируем результат запроса, возвращающий существующего пользователя
        mock_user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            password="hashed_password"
        )
        
        mock_result = MagicMock()
        mock_result.scalar.return_value = mock_user
        
        # Создаем мок для execute метода с правильным возвратом result
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.return_value = mock_result
        
        # Мокируем функцию decode_token
        with patch("src.auth.handlers.decode_token") as mock_decode:
            mock_decode.return_value = {"sub": "test@example.com"}
            
            # Вызываем тестируемую функцию
            result = await get_current_user("valid.jwt.token", mock_db)
            
            # Проверяем результат
            assert result is mock_user
            
            # Проверяем, что decode_token был вызван с правильными параметрами
            mock_decode.assert_called_once_with("valid.jwt.token")

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Тест получения текущего пользователя с невалидным токеном"""
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Мокируем функцию decode_token для имитации JWTError
        with patch("src.auth.handlers.decode_token") as mock_decode:
            # Имитируем исключение при декодировании
            mock_decode.side_effect = JWTError("Invalid token")
            
            # Проверяем, что вызывается исключение
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("invalid.jwt.token", mock_db)
            
            # Проверяем параметры исключения
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid token"

    @pytest.mark.asyncio
    async def test_get_current_user_missing_sub(self):
        """Тест получения текущего пользователя с токеном без sub"""
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Мокируем функцию decode_token для возврата payload без sub
        with patch("src.auth.handlers.decode_token") as mock_decode:
            mock_decode.return_value = {}  # Пустой payload без sub
            
            # Проверяем, что вызывается исключение
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("invalid.jwt.token", mock_db)
            
            # Проверяем параметры исключения
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid token" 