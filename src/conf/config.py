from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    secret_key: str
    redis_url: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    mail_username: str
    mail_password: str
    mail_server: str
    mail_port: int
    mail_from: str

    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    class Config:
        env_file = ENV_FILE
        env_file_encoding = "utf-8"


settings = Settings()
