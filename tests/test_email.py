import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from email.message import EmailMessage

from src.services.email import send_verification_email, send_reset_password_email
from src.conf.config import settings


class TestEmail:
    """Тесты для сервиса отправки email"""
    
    @pytest.mark.asyncio
    async def test_send_verification_email(self):
        """Тест отправки email верификации"""
        # Тестовые данные
        test_email = "test@example.com"
        test_token = "verification-token-123"
        
        # Мокируем функцию отправки email
        with patch("aiosmtplib.send", new_callable=AsyncMock) as mock_send:
            # Вызываем тестируемую функцию
            await send_verification_email(test_email, test_token)
            
            # Проверяем, что функция отправки была вызвана
            mock_send.assert_called_once()
            
            # Проверяем аргументы, с которыми была вызвана функция
            args, kwargs = mock_send.call_args
            message = args[0]
            
            # Проверяем параметры сообщения
            assert isinstance(message, EmailMessage)
            assert message["From"] == settings.mail_from
            assert message["To"] == test_email
            assert message["Subject"] == "Verify your email"
            
            # Проверяем содержимое сообщения
            content = message.get_content()
            assert f"http://localhost:8000/api/auth/verify/{test_token}" in content
            
            # Проверяем параметры SMTP
            assert kwargs["hostname"] == settings.mail_server
            assert kwargs["port"] == settings.mail_port
            assert kwargs["username"] == settings.mail_username
            assert kwargs["password"] == settings.mail_password
            assert kwargs["start_tls"] == True
            assert kwargs["validate_certs"] == False
    
    @pytest.mark.asyncio
    async def test_send_reset_password_email(self):
        """Тест отправки email для сброса пароля"""
        # Тестовые данные
        test_email = "test@example.com"
        test_token = "reset-token-123"
        
        # Мокируем функцию отправки email
        with patch("aiosmtplib.send", new_callable=AsyncMock) as mock_send:
            # Вызываем тестируемую функцию
            await send_reset_password_email(test_email, test_token)
            
            # Проверяем, что функция отправки была вызвана
            mock_send.assert_called_once()
            
            # Проверяем аргументы, с которыми была вызвана функция
            args, kwargs = mock_send.call_args
            message = args[0]
            
            # Проверяем параметры сообщения
            assert isinstance(message, EmailMessage)
            assert message["From"] == settings.mail_from
            assert message["To"] == test_email
            assert message["Subject"] == "Password Reset Request"
            
            # Проверяем параметры SMTP
            assert kwargs["hostname"] == settings.mail_server
            assert kwargs["port"] == settings.mail_port
            assert kwargs["username"] == settings.mail_username
            assert kwargs["password"] == settings.mail_password
            assert kwargs["start_tls"] == True
            assert kwargs["validate_certs"] == False 