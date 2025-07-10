from fastapi import APIRouter

from .schemas import UserSchema, UserCreateSchema
from ..database import database, models


router = APIRouter()


@router.post("/user")
async def add_user(user: UserCreateSchema, session: database.SessionDep):
    new_user = models.User(
        username = user.username
    )
    session.add(new_user)
    await session.commit()
