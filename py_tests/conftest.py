"""
conftest.py - стандартный файл c "настройками" для pytest-тестов.
Помимо фиксур здесь еще будут лежать три класса:
1) Password - хэширует пароли и проверяет хэши.
2) Token - хранит полученные токены и выдает их обратно.
3) Socket - выдает сокет по запросу.
"""
import pytest
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from ..app.config import settings


class Password:
    """
    Класс для выдачи и провеки хэшей.
    """
    pwd_context = CryptContext(
        schemes=["bcrypt", "sha256_crypt"],
        deprecated="auto"
    )

    def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        """
        Проверяем валидность хэша через сравнение хэшей
        введенного пароля и сохраненного в БД пароля.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(
        self, plain_password: str
    ) -> str:
        """
        Делаем хэш из чистого пароля.
        """
        return self.pwd_context.hash(plain_password)


class Token:
    """
    Класс для выдачи и хранения токена.
    """
    _token = None

    @property
    def token(self):
        """
        Если токен был передан классу, то
        распаковываем словарь, в котором он был
        передан и записываем значения в строку.
        """
        if self._token:
            token_type = self._token.get("token_type", None)
            access_token = self._token.get("access_token", None)
            return f'{token_type} {access_token}'
    
    @token.setter
    def token(self, value):
        """
        Задаем значение токену.
        """
        self._token = value


class Socket:
    """
    Класс для выдачи сокета.
    """
    host = '127.0.0.1'
    port = '8000'

    @property
    def socket(self):
        """
        Формируем URL.
        """
        return f"http://{self.host}:{self.port}"


@pytest.fixture
async def session():
    """
    Создаем в фиксуре движок и делаем сессию.
    """
    engine = create_async_engine(settings.postgres_url)
    async with engine.begin():
        async_session_maker = async_sessionmaker(
            bind=engine, expire_on_commit=False
        )
        async with async_session_maker() as session_m:
            yield session_m


socket = Socket()
password = Password()
token = Token()

TIMEOUT = 300
