import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_app_routes_coverage():

    routes = [route for route in app.routes]
    assert len(routes) > 0, "В приложении должны быть зарегистрированы роуты"
    
    contacts_routes = [route for route in app.routes if route.path.startswith("/contacts")]
    assert len(contacts_routes) > 0, "Роуты для контактов должны быть зарегистрированы"
    
    # Проверяем, что роуты auth зарегистрированы
    auth_routes = [route for route in app.routes if route.path.startswith("/api/auth")]
    assert len(auth_routes) > 0, "Роуты для авторизации должны быть зарегистрированы" 