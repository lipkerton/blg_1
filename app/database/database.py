from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import Depends

from typing import Annotated

from app.config import settings
from .models import Base


engine = create_async_engine(settings.POSTGRES_URL)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_session():
    async with async_session_maker() as session:
        yield session


async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


SessionDep = Annotated[AsyncSession, Depends(get_session)]
