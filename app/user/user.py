from typing import Annotated

from sqlalchemy import select
from fastapi import APIRouter, Depends

from .schemas import UserGetSchema, UserCreateSchema
from .basic_auth import get_password_hash, credentials_check
from ..database import database, models


router = APIRouter()


@router.get("/user/{index:int}", response_model=UserGetSchema)
async def get_user(
    index: int,
    session: database.SessionDep,
    credentials: Annotated[tuple[str], Depends(credentials_check)]
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

