Introduction
============

This is documentation for a FastAPI application that provides a contact management service with authentication and email verification.

Key Features
-----------

* Registration and login using JWT (access + refresh tokens)
* Email verification via external mail service
* CRUD operations for contacts
* Avatar uploads
* Protected endpoints with access restrictions
* Password hashing
* Docker and Docker Compose support

Technology Stack
--------------

* Python 3.9+
* FastAPI
* PostgreSQL (via SQLAlchemy)
* Redis (for storing refresh tokens)
* Docker / Docker Compose
* Cloudinary (image storage)
* Jinja2 (templating) 