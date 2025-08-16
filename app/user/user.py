"""
Методы и эндпоинты, которые связаны с юзерами.
Сделано:
1) Метод для создания пользователя
2) Метод для логина пользователя.
3) Метод для получения списка пользователей.
4) Метод для получения конкретного пользователя.
5) Метод для удаления пользователя.
"""
from typing import Annotated

from sqlalchemy import select, delete
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials

from .schemas import UserGetSchema, UserCreateSchema, Token
from .basic_auth import get_password_hash, credentials_check
from .jwt_token_auth import create_jwt_token, token_check
from ..database import database, models


router = APIRouter()

CredentialsBasic = Annotated[HTTPBasicCredentials, Depends(credentials_check)]
CredentialsToken = Annotated[dict, Depends(token_check)]


@router.post("/login", response_model=Token)
async def login(
    credentials: CredentialsBasic
):
    """
    Проверяем юзернейм и пароль,
    если они подходят - возвращаем токен.
    """
    jwt_token = create_jwt_token(
        {
        "username": credentials.username,
        "password": credentials.password
        }
    )
    return {"access_token": jwt_token, "token_type": "Bearer"}


@router.get("/user", response_model=list[UserGetSchema])
async def get_users(
    session: database.SessionDep,
    credentials: CredentialsToken  # pylint: disable=unused-argument
):
    """
    Через SELECT получаем всех пользователей.
    """
    query = select(
        models.User.user_id,
        models.User.username,
        models.User.email
    )
    result = await session.execute(query)
    return result.all()


@router.get("/user/{username:str}", response_model=UserGetSchema)
async def get_user(
    username: str,
    session: database.SessionDep,
    credentials: CredentialsToken  # pylint: disable=unused-argument
):
    """
    Через SELECT получем пользователя
    с юзернеймом из параметра пути.
    """
    query = select(
        models.User.user_id,
        models.User.username,
        models.User.email,
    )
    query = query.where(
        models.User.username == username
    )
    result = await session.execute(query)
    return result.one()


@router.post("/user")
async def add_user(
    user: UserCreateSchema,
    session: database.SessionDep
):
    """
    Добавляем нового юзера в БД.
    """
    hashed_password = get_password_hash(
        user.password
    )
    new_user = models.User(
        username = user.username,
        password = hashed_password,
        email = user.email
    )
    session.add(new_user)
    await session.commit()


@router.delete("/user/{username:str}")
async def delete_user(
    username: str,
    session: database.SessionDep,
    credentials: CredentialsToken  # pylint: disable=unused-argument
):
    """
    Удаляем пользователя с юзернеймом
    из параметра пути.
    """
    query = delete(models.User).where(
        models.User.username == username
    )
    await session.execute(query)
    await session.commit()
