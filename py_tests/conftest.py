import pytest
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from ..app.config import settings


class Password:

    pwd_context = CryptContext(
        schemes=["bcrypt", "sha256_crypt"],
        deprecated="auto"
    )

    def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(
        self, password: str
    ) -> str:
        return self.pwd_context.hash(password)


class Token:

    _token = None

    @property
    def token(self):
        if self._token:
            token_type = self._token.get("token_type", None)
            access_token = self._token.get("access_token", None)
            return f'{token_type} {access_token}'


@pytest.fixture
def socket():
    host = '127.0.0.1'
    port = '8000'
    yield f"http://{host}:{port}"


@pytest.fixture
async def session():
    engine = create_async_engine(settings.POSTGRES_URL)
    async with engine.begin() as conn:
        async_session_maker = async_sessionmaker(
            bind=engine, expire_on_commit=False
        )
        async with async_session_maker() as session:
            yield session


password = Password()
token = Token()

