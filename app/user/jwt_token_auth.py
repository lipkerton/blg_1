"""
Здесь я очень сильно старался сделать
аутентификацию по JWT токену.
"""
from typing import Annotated
from datetime import datetime, timezone, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy import select

from ..config import settings
from .schemas import UserGetSchema
from ..database import database, models

security = HTTPBearer()

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 30

CredentialsSecurity = Annotated[str, Depends(security)]


def create_jwt_token(data: dict) -> str:
    """
    Создаем и возвращаем JWT токен из данных, которые
    передаются из метода `/login`.
    """
    expire = (
        datetime.now(timezone.utc)
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    data.update({"exp": expire})
    jwt_token = jwt.encode(
        data, SECRET_KEY, algorithm=ALGORITHM
    )
    return jwt_token


def verify_jwt_token(jwt_token: str) -> dict | None:
    """
    Проверяем JWT токен.
    """
    try:
        decoded_jwt_token = jwt.decode(
            jwt_token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        expire = decoded_jwt_token.get("exp", None)
        if (
            expire
            and datetime.fromtimestamp(expire)
            >= datetime.utcnow()
        ):
            return decoded_jwt_token
        return None
    except jwt.PyJWTError:
        return None


async def token_check(
    credentials: CredentialsSecurity,
    session: database.SessionDep
):
    """
    Эта функция нужна, чтобы сделать зависимость с ней
    из user-методов - она получает кредиты и отправляет
    токен на проверку.
    Если проверка прошла успешно, то функция возвращает
    объект юзера из БД, пропущенный через Pydantic-схему.
    """
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid or expired token",
        headers={"WWW-authenticate": "Bearer"}
    )
    jwt_token = credentials.credentials  # type: ignore
    payload = verify_jwt_token(jwt_token)

    if payload:
        query = select(
            models.User.user_id,
            models.User.username,
            models.User.email
        ).where(
            models.User.username == payload.get("username")
        )
        user = await session.execute(query)
        user = UserGetSchema.model_validate(user.one())
        return user
    raise unauthed_exc
