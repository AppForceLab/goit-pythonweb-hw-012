import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import tempfile
import io
import uuid

from src.services.cloudinary_service import upload_avatar
from fastapi import UploadFile


@pytest.mark.asyncio
async def test_upload_avatar():
    """
    Тест загрузки аватара в Cloudinary
    """
    # Создаем временный файл для тестирования
    with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_file:
        # Создаем тестовые данные
        file_content = b"test image content"
        temp_file.write(file_content)
        temp_file.flush()
        
        # Создаем объект UploadFile
        file = MagicMock(spec=UploadFile)
        file.filename = "test_avatar.jpg"
        
        # Мокируем чтение файла
        file.read = AsyncMock(return_value=file_content)
        
        # Мокируем cloudinary.uploader.upload
        mock_upload_result = {
            "secure_url": "https://cloudinary.com/test_avatar.jpg"
        }
        
        # Патчим функцию uuid4, чтобы она всегда возвращала один и тот же id
        with patch("uuid.uuid4", return_value=uuid.UUID("00000000-0000-0000-0000-000000000000")):
            # Патчим cloudinary.uploader.upload
            with patch("cloudinary.uploader.upload", return_value=mock_upload_result):
                # Вызываем функцию загрузки аватара
                result = await upload_avatar(file)
                
                # Проверяем результат
                assert result == "https://cloudinary.com/test_avatar.jpg"
                
                # Проверяем, что файл был прочитан
                assert file.read.called 