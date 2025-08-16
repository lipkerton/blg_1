"""
Модели проекта, по которым должны быть
созданы миграции + сущности в БД.
1) сделана модель юзера.
2) сделана модель для постов.
"""
from datetime import datetime, timezone
from secrets import token_hex

from sqlalchemy import TIMESTAMP, BigInteger, String, Text, CheckConstraint, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Базовый класс для создания
    пользовательских моделей.
    """

class User(Base):
    """
    Класс описывает таблицу `users`.
    """
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(200), unique=True)
    password: Mapped[str] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(
        String(200), unique=True, default=None
    )
    static_token: Mapped[str] = mapped_column(
        String(200), unique=True, default=token_hex(16)
    )

    __table_args__ = (
        CheckConstraint("length(username) > 0", name="chk_length_username"),
    )



class Post(Base):
    """
    Класс описывает таблицу `posts`.
    """
    __tablename__ = "posts"

    post_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    content: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="cascade")
    )

    __table_args__ = (
        CheckConstraint("length(title) > 0", name="chk_length_title"),
        CheckConstraint("length(content) > 0", name="chk_length_content")
    )
