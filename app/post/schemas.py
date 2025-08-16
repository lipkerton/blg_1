"""
Pydantic модели для post.py
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr


class PostGetSchema(BaseModel):
    """
    reponse_model для методов `get_post` и `get_posts`.
    Сериализует данные, которые возвращает ORM запрос.
    """
    post_id: int
    username: str
    email: EmailStr | None = None
    created_at: datetime
    title: str
    content: str

    class Config:
        """
        Настройка, которая позволяет схеме сериализовать ORM-объекты
        (нужна, чтобы response_model работала корректно).
        """
        from_attributes = True


class PostCreateSchema(BaseModel):
    """
    Схема валидирует данные, которые пришли с POST
    запросом на создание поста.
    """
    title: str
    content: str
