from typing import Annotated

from sqlalchemy import select
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials

from .schemas import UserGetSchema, UserCreateSchema, Token
from .basic_auth import get_password_hash, credentials_check
from .jwt_token_auth import create_jwt_token, token_check
from ..database import database, models


router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    credentials: Annotated[HTTPBasicCredentials, Depends(credentials_check)]
):
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
    credentials: Annotated[dict, Depends(token_check)]
):
    query = select(
        models.User.user_id,
        models.User.username,
        models.User.email
    )
    result = await session.execute(query)
    return result.all()


@router.get("/user/{index:int}", response_model=UserGetSchema)
async def get_user(
    index: int,
    session: database.SessionDep,
):
    query = select(
        models.User.user_id,
        models.User.username,
        models.User.email,
    )
    query = query.where(
        models.User.user_id == index
    )
    result = await session.execute(query)
    return result.one()


@router.post("/user")
async def add_user(
    user: UserCreateSchema,
    session: database.SessionDep
):
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
