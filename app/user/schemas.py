"""
Pydantic модели для user.py
"""
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """
    response_model для метода `login`.
    Проверяет словарь с токеном. 
    """
    access_token: str
    token_type: str


class UserGetSchema(BaseModel):
    """
    reponse_model для методов `get_user` и `get_users`.
    Сериализует данные, которые возвращает ORM запрос.
    """
    user_id: int
    username: str
    email: EmailStr | None = None

    class Config:
        """
        Настройка, которая позволяет схеме сериализовать ORM-объекты
        (нужна, чтобы response_model работала корректно).
        """
        from_attributes = True


class UserCreateSchema(BaseModel):
    """
    Схема валидирует данные, которые приходят
    POST-запросом на создание пользователя.
    """
    username: str
    password: str
    email: EmailStr | None = None
