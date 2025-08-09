from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
import pytest

from ..app.config import settings


pytestmark = pytest.mark.db


def test_engine():
    engine = create_async_engine(settings.POSTGRES_URL)
    assert isinstance(engine, AsyncEngine), \
        f"Не удалось подключиться к БД с помощью запроса: {settings.POSTGRES_URL}."


async def test_session():
    engine = create_async_engine(settings.POSTGRES_URL)
    async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with async_session_maker() as session:
        assert isinstance(session, AsyncSession), \
            "Ошибка при попытке создать сессию."


async def test_query(session):
    query = select(1)
    result = await session.execute(query)
    assert result.scalar() == 1, \
        "Запрос `select(1)` вернул неверный результат."


