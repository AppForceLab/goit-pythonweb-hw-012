FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl build-essential \
  && curl -sSL https://install.python-poetry.org | python3 - \
  && ln -s /root/.local/bin/poetry /usr/local/bin/poetry \
  && apt-get clean

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false \
  && poetry install --no-root --only main

COPY . /app

CMD ["fastapi", "dev"]

