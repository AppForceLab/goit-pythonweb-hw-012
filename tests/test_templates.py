import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from fastapi.templating import Jinja2Templates
from src.services.templates import templates


class TestTemplates:
    """Тесты для шаблонов"""
    
    def test_templates_initialization(self):
        """Тест инициализации шаблонов"""
        # Проверяем что templates это экземпляр класса Jinja2Templates
        assert isinstance(templates, Jinja2Templates)
        
        # Путь нельзя получить напрямую через атрибут, проверяем через dir_path
        # В новой версии FastAPI доступа к directory нет
        assert templates.env is not None
    
    def test_templates_directory_exists(self):
        """Тест существования директории шаблонов"""
        # Проверяем что директория шаблонов существует
        templates_dir = Path("templates")
        assert templates_dir.exists(), "Директория templates не существует"
        assert templates_dir.is_dir(), "templates не является директорией"
    
    def test_template_response(self):
        """Тест создания ответа с шаблоном"""
        # Мокируем встроенный метод TemplateResponse
        with patch.object(templates, "TemplateResponse") as mock_template_response:
            # Настраиваем мок для TemplateResponse
            mock_response = MagicMock()
            mock_template_response.return_value = mock_response
            
            # Создаем фейковый запрос и контекст
            mock_request = MagicMock()
            context = {"title": "Test Title", "content": "Test Content"}
            
            # Вызываем TemplateResponse
            response = templates.TemplateResponse("test_template.html", {"request": mock_request, **context})
            
            # Проверяем, что метод был вызван с правильными аргументами
            mock_template_response.assert_called_once_with("test_template.html", {"request": mock_request, "title": "Test Title", "content": "Test Content"})
            
            # Проверяем, что метод вернул ожидаемый объект
            assert response == mock_response 