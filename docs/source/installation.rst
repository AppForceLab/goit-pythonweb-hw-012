Installation and Setup
===================

Cloning the Project
-----------------

.. code-block:: bash

    git clone https://github.com/AppForceLab/goit-pythonweb-hw-10.git
    cd goit-pythonweb-hw-10

Environment Variables Setup
-------------------------

Create a `.env` file in the project root:

.. code-block:: env

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

Installation with Docker
---------------------

.. code-block:: bash

    docker-compose up --build

API Documentation Access
---------------------

After starting the application, the documentation will be available at:

* Swagger UI: http://localhost:8000/docs 