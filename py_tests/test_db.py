"""
Тесты для первичной провеки коннекта к БД.
"""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from ..app.config import settings

pytestmark = pytest.mark.db


def test_engine():
    """
    Делаем движок + проверяем, что он был создан.
    """
    engine = create_async_engine(settings.postgres_url)
    assert isinstance(engine, AsyncEngine), \
        f"Не удалось подключиться к БД с помощью запроса: {settings.postgres_url}."


async def test_session():
    """
    Снова делаем движок + от него делаем сессию
    и проверяем, что сессия была создана.
    """
    engine = create_async_engine(settings.postgres_url)
    async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with async_session_maker() as session:
        assert isinstance(session, AsyncSession), \
            "Ошибка при попытке создать сессию."


async def test_query(session):
    """
    Делаем ORM запрос к БД на проверку работы.
    """
    query = select(1)
    result = await session.execute(query)
    assert result.scalar() == 1, \
        "Запрос `select(1)` вернул неверный результат."
