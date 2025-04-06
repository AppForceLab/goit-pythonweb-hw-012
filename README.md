📱 **Контакт-менеджер с авторизацией и email-подтверждением**, реализованный на FastAPI + PostgreSQL + Redis + Docker.

## 🚀 Возможности

- 🔐 Регистрация и вход через JWT (access + refresh tokens)
- ✅ Подтверждение email через внешнюю почтовую службу
- 🧾 CRUD операции только для своих контактов
- 📸 Загрузка аватарки на Cloudinary
- 🧠 Ограничение доступа к эндпоинту `/me`
- 🧂 Хеширование паролей
- 📦 Docker + Docker Compose
- 🌐 Swagger UI (доступен по адресу `/docs`)

---

## ⚙️ Стек технологий

- Python 3.12
- FastAPI
- PostgreSQL (через SQLAlchemy)
- Redis (для хранения refresh-токенов)
- Docker / Docker Compose
- Cloudinary (хранение изображений)
- dotenv (управление переменными окружения)

---

## 🛠 Установка и запуск

### 📁 Клонировать проект

```bash
git clone https://github.com/AppForceLab/goit-pythonweb-hw-10.git
cd goit-pythonweb-hw-10

⚙️ Настроить переменные окружения
Создай .env файл по примеру:

env
Copy
Edit
POSTGRES_DB=your_db
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
DATABASE_URL=postgresql://your_user:your_password@db:5432/your_db
SECRET_KEY=your_secret_key
REDIS_URL=redis://redis:6379

EMAIL_HOST=smtp.your-email.com
EMAIL_PORT=587
EMAIL_USER=your_email
EMAIL_PASSWORD=your_password

CLOUDINARY_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_key
CLOUDINARY_API_SECRET=your_secret

🐳 Запуск через Docker Compose
docker-compose up --build

Документация будет доступна по адресу:
Swagger UI: http://localhost:8000/docs