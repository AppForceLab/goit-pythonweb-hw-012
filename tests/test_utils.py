import pytest
from unittest.mock import patch, MagicMock
import datetime
from datetime import date, datetime, timedelta

from src.auth.hashing import pwd_context, verify_password, hash_password
from src.auth.jwt_utils import create_access_token, create_refresh_token
from src.utils.datetime_utils import convert_birthday, get_upcoming_birthdays, days_to_birthday, format_date


def test_verify_password():
    # Создаем хэш для тестового пароля
    hashed = pwd_context.hash("testpassword")
    
    # Проверяем правильный пароль
    assert verify_password("testpassword", hashed) is True
    
    # Проверяем неправильный пароль
    assert verify_password("wrongpassword", hashed) is False


def test_hash_password():
    # Хешируем пароль
    hashed = hash_password("testpassword")
    
    # Проверяем, что хеш не совпадает с исходным паролем
    assert hashed != "testpassword"
    
    # Проверяем, что пароль может быть верифицирован
    assert verify_password("testpassword", hashed)


def test_create_access_token():
    # Патчим datetime, чтобы токены всегда были разные
    with patch('src.auth.jwt_utils.datetime') as mock_datetime:
        mock_datetime.utcnow.side_effect = [
            datetime(2023, 1, 1, 12, 0, 0),
            datetime(2023, 1, 1, 12, 1, 0)  # Разное время для разных токенов
        ]
        mock_datetime.timedelta = timedelta
        
        # Создаем тестовый токен
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Проверяем, что токен не пустой
        assert token
        assert isinstance(token, str)
        
        # Токены должны быть разными при каждой генерации
        token2 = create_access_token(data)
        assert token != token2


def test_create_refresh_token():
    # Патчим datetime, чтобы токены всегда были разные
    with patch('src.auth.jwt_utils.datetime') as mock_datetime:
        mock_datetime.utcnow.side_effect = [
            datetime(2023, 1, 1, 12, 0, 0),
            datetime(2023, 1, 1, 12, 1, 0)  # Разное время для разных токенов
        ]
        mock_datetime.timedelta = timedelta
        
        # Создаем тестовый токен
        data = {"sub": "test@example.com"}
        token = create_refresh_token(data)
        
        # Проверяем, что токен не пустой
        assert token
        assert isinstance(token, str)
        
        # Токены должны быть разными при каждой генерации
        token2 = create_refresh_token(data)
        assert token != token2


def test_get_upcoming_birthdays():
    # Создаем список тестовых дней рождения
    today = date.today()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=6)
    next_month = today + timedelta(days=30)
    
    birthdays = [today, tomorrow, next_week, next_month]
    
    # Проверяем с дефолтным периодом (7 дней)
    upcoming = get_upcoming_birthdays(birthdays)
    assert len(upcoming) == 3  # сегодня, завтра и через неделю
    
    # Проверяем с другим периодом
    upcoming_month = get_upcoming_birthdays(birthdays, days=30)
    assert len(upcoming_month) == 4  # все четыре в пределах месяца


class TestDatetimeUtils:
    """Тесты для утилит работы с датами"""
    
    def test_days_to_birthday(self):
        """Тест расчета дней до дня рождения"""
        # Тестируем функциональность без моков
        # Берем текущую дату
        today = date.today()
        
        # День рождения сегодня
        today_birthday = date(today.year - 20, today.month, today.day)
        assert days_to_birthday(today_birthday) == 0
        
        # Проверим другие сценарии, которые невозможно точно предсказать 
        # из-за зависимости от текущей даты, но можем проверить диапазон
        
        # День рождения - результат должен быть неотрицательным числом
        some_date = date(1990, 1, 1)
        days = days_to_birthday(some_date)
        assert isinstance(days, int)
        assert 0 <= days < 366  # максимум 365 дней для обычного года или 366 для високосного
    
    def test_convert_birthday(self):
        """Тест конвертации строки в объект даты"""
        # Стандартный формат ISO
        assert convert_birthday("2023-06-15") == date(2023, 6, 15)
        
        # Невалидная дата
        with pytest.raises(ValueError):
            convert_birthday("not-a-date")
    
    def test_format_date(self):
        """Тест форматирования даты в строку"""
        test_date = date(2023, 6, 15)
        
        # Стандартный формат
        assert format_date(test_date) == "15.06.2023"
        
        # Другие форматы
        assert format_date(test_date, "%d/%m/%Y") == "15/06/2023"
        assert format_date(test_date, "%B %d, %Y") == "June 15, 2023"
        
        # Форматирование None
        assert format_date(None) == "" 