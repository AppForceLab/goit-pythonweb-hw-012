import pytest
from fastapi.testclient import TestClient

def test_app_health(client: TestClient):
    """Тест проверки работоспособности приложения"""
    response = client.get("/")
    assert response.status_code == 404  # Если корневой маршрут не определен
    # Если корневой маршрут определен, используйте следующий код:
    # assert response.status_code == 200
    
    # Проверяем заголовки ответа (JSON или HTML)
    assert "application/json" in response.headers.get("content-type", "") or "text/html" in response.headers.get("content-type", "") 