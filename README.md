# 📱 Contact Management REST API

A FastAPI-based REST API for contact management with authentication, email verification, and role-based access control.

## 📌 Project Description

This application provides a comprehensive contact management system with modern authentication features including:

- User registration and login with JWT authentication
- Email verification for new users
- Password reset functionality via email
- Role-based access control (user/admin)
- CRUD operations for contacts
- User avatar uploads
- Test coverage and documentation

## ⚙️ Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis
- **Authentication**: JWT (access + refresh tokens)
- **Email**: SMTP integration
- **Image Storage**: Cloudinary
- **Containerization**: Docker & Docker Compose
- **Testing**: Pytest, Pytest-cov, Httpx AsyncClient
- **Documentation**: Swagger UI, Sphinx
- **Template Engine**: Jinja2

## 📂 Project Structure

```
.
├── alembic/              # Database migrations
├── docs/                 # Sphinx documentation
├── src/                  # Application source code
│   ├── api/              # API routes and endpoints
│   ├── auth/             # Authentication utilities
│   ├── conf/             # Configuration
│   ├── database/         # Database models and connection
│   ├── repository/       # Data access layer
│   ├── schemas/          # Pydantic models
│   ├── services/         # Business logic
│   └── utils/            # Utility functions
├── templates/            # Email and HTML templates
├── tests/                # Test suite
│   ├── conftest.py       # Test fixtures
│   ├── test_integration_*.py  # Integration tests
│   └── test_*.py         # Unit tests
├── .env                  # Environment variables (not in Git)
├── docker-compose.yml    # Docker configuration
├── Dockerfile            # Container definition
├── pyproject.toml        # Dependencies (Poetry)
└── README.md             # This documentation
```

## ✅ Completed Requirements

### 📄 Sphinx Documentation Generation
- Implemented Google-style docstrings across the codebase
- Generated comprehensive HTML documentation using Sphinx
- Auto-documented all API endpoints, services, and models

### 🧪 Repository Unit Testing
- Created unit tests for all repository methods
- Implemented mocks for database dependencies
- Tested success and error scenarios for data access

### 🔌 API Integration Testing
- Set up integration tests for all API routes using httpx.AsyncClient
- Created test fixtures with SQLite in-memory database
- Used mocks for external services (Redis, email)

### 📊 Test Coverage (>75%)
- Achieved over 75% test coverage
- Used pytest-cov for coverage reporting
- Prioritized testing for critical paths and edge cases

### 🔄 Redis Caching
- Implemented Redis caching for the current user
- Reduced database queries for authenticated requests
- Used JSON serialization for user data storage

### 🔑 Password Reset via Email
- Created password reset request endpoint
- Implemented secure token generation and verification
- Added email templates for reset instructions

### 👤 Role-based Authorization
- Implemented user roles (user/admin)
- Added permission checks on protected endpoints
- Created admin-only features (e.g., avatar management)

### 🔐 Access/Refresh Token Authentication
- Implemented JWT access tokens with short expiry
- Added refresh tokens for session persistence
- Created secure token refresh mechanism

## 🧪 Testing

### Coverage Report

```
Name                       Stmts   Miss  Cover
----------------------------------------------
src/api/auth.py              120     22    82%
src/api/contacts.py           75     14    81%
src/repository/contacts.py    45      7    84%
src/services/auth.py          35      5    86%
src/services/email.py         25      2    92%
...
TOTAL                        485    116    76%
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src

# Run specific test files
pytest tests/test_integration_auth.py

# Run with verbose output
pytest -v
```

## 📘 Documentation

The documentation is generated using Sphinx with autodoc, napoleon, and viewcode extensions.

### Generation Steps

1. Write Google-style docstrings in Python code
2. Run sphinx-quickstart to set up documentation structure
3. Configure autodoc to extract documentation from docstrings
4. Build HTML documentation with sphinx-build

### Access Documentation

After building, HTML documentation is available in `docs/build/` directory:

```bash
# Generate documentation
cd docs && poetry run sphinx-build -b html source build

# View documentation (open docs/build/index.html in browser)
```

## 🐳 Containerization

The application uses Docker Compose for easy deployment with the following services:

- **app**: FastAPI application
- **db**: PostgreSQL database
- **redis**: Redis cache server

### Running with Docker

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# Stop all services
docker-compose down
```

## 🔐 Environment Setup

Sensitive information is stored in a `.env` file (not included in the repository):

```
# Database
POSTGRES_DB=your_db
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
DATABASE_URL=postgresql://your_user:your_password@db:5432/your_db

# Security
SECRET_KEY=your_secret_key

# Redis
REDIS_URL=redis://redis:6379

# Email
EMAIL_HOST=smtp.your-email.com
EMAIL_PORT=587
EMAIL_USER=your_email
EMAIL_PASSWORD=your_password

# Cloudinary
CLOUDINARY_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_key
CLOUDINARY_API_SECRET=your_secret
```

Create a `.env` file with these variables before running the application.

## 🚀 Getting Started

1. Clone the repository
2. Create a `.env` file using the template above
3. Run with Docker: `docker-compose up`
4. Access API at http://localhost:8000
5. View API documentation at http://localhost:8000/docs