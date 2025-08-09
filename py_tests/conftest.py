import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from ..app.config import settings


@pytest.fixture
def socket():
    host = '127.0.0.1'
    port = '8000'
    return f"http://{host}:{port}"


@pytest.fixture
async def session():
    engine = create_async_engine(settings.POSTGRES_URL)
    async with engine.begin() as conn:
        async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
        async with async_session_maker() as session:
            yield session
