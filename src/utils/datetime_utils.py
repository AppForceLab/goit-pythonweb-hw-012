from datetime import datetime, date, timedelta
from typing import List, Optional


def convert_birthday(birthday_str: str) -> date:
    """
    Конвертирует строку с датой рождения в объект date.
    
    Args:
        birthday_str: Строка с датой в формате YYYY-MM-DD
        
    Returns:
        Объект datetime.date
        
    Raises:
        ValueError: Если строка имеет неправильный формат
    """
    try:
        return datetime.strptime(birthday_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Некорректный формат даты: {birthday_str}. Ожидается формат YYYY-MM-DD")


def get_upcoming_birthdays(birthdays: List[date], days: int = 7) -> List[date]:
    """
    Возвращает список дней рождения, которые наступят в ближайшие n дней.
    
    Args:
        birthdays: Список дат рождения
        days: Количество дней для проверки (по умолчанию 7)
        
    Returns:
        Список дат рождения в ближайшие дни
    """
    today = date.today()
    end_date = today + timedelta(days=days)
    
    # Фильтруем даты, которые попадают в указанный период
    upcoming = [b for b in birthdays if today <= b <= end_date]
    
    return upcoming


def format_date(d: Optional[date], format_str: str = "%d.%m.%Y") -> str:
    """
    Форматирует дату в строку по указанному формату.
    
    Args:
        d: Объект datetime.date
        format_str: Строка формата (по умолчанию DD.MM.YYYY)
        
    Returns:
        Отформатированная строка с датой
    """
    if d is None:
        return ""
    return d.strftime(format_str)


def days_to_birthday(birthday: date) -> int:
    """
    Вычисляет количество дней до следующего дня рождения.
    
    Args:
        birthday: Дата рождения
    
    Returns:
        Количество дней до следующего дня рождения
    """
    today = date.today()
    next_birthday = date(today.year, birthday.month, birthday.day)
    
    # Если день рождения в этом году уже прошел, берем следующий год
    if next_birthday < today:
        next_birthday = date(today.year + 1, birthday.month, birthday.day)
    
    delta = next_birthday - today
    return delta.days 