"""
Здесь хранится класс, который забирает
секреты из `.env` и помогает создавать
строки для подключения к БД и прч.
"""
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()

class Settings(BaseSettings):
    """
    Класс для хранения настроек проекта
    в том числе для хранения секретов (из .env).

    """
    POSTGRES_DB_HOST: str
    POSTGRES_DB_NAME: str
    POSTGRES_DB_USER: str
    POSTGRES_DB_PASS: str
    POSTGRES_DB_PORT: int

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    BASE_DIR: Path = Path('.').absolute()
    TEMPLATES_DIR: Path = BASE_DIR / "app/templates"
    STATIC_DIR: Path = BASE_DIR / "app/static"

    @property
    def postgres_url(self):
        """
        Ссылка для создания асинхронного движка.
        """
        return (
            f"postgresql+asyncpg://{self.POSTGRES_DB_USER}:{self.POSTGRES_DB_PASS}"
            f"@{self.POSTGRES_DB_HOST}:{self.POSTGRES_DB_PORT}/{self.POSTGRES_DB_NAME}"
        )

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")

settings: Settings = Settings() # type: ignore
