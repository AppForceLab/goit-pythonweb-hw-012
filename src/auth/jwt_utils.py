from datetime import datetime, timedelta
from jose import jwt as jose_jwt
from src.conf.config import settings


def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jose_jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(data: dict):
    return create_token(data, timedelta(minutes=settings.access_token_expire_minutes))


def create_refresh_token(data: dict):
    return create_token(data, timedelta(days=settings.refresh_token_expire_days))


def decode_token(token: str):
    return jose_jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
