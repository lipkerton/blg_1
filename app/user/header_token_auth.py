from typing import Annotated

from fastapi import Header, HTTPException, status
from sqlalchemy import select

from ..database import database, models


async def static_token_check(
    static_token: Annotated[str, Header(alias="x-auth-token")],
    session: database.SessionDep
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid token"
    )
    query = select(
        models.User.username,
        models.User.static_token
    ).where(
        models.User.static_token == static_token
    )
    db_credentials = await session.execute(query)
    db_credentials = db_credentials.one_or_none()
    if db_credentials:
        return db_credentials
    raise unauthed_exc



