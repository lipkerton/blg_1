from typing import Annotated

from sqlalchemy import select, update
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from ..database import database, models


security = HTTPBasic()
pwd_context = CryptContext(
    schemes=["bcrypt", "sha256_crypt"], deprecated="auto"
)


def verify_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, str | None]:
    return pwd_context.verify_and_update(plain_password, hashed_password)


def get_password_hash(
    password: str
) -> str:
    return pwd_context.hash(password)


async def credentials_check(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    session: database.SessionDep,
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
        headers={"WWW-Authenticate": "Basic"}
    )
    
    query = select(
        models.User.username,
        models.User.password
    ).where(
        models.User.username == credentials.username
    )
    db_credentials = await session.execute(query)
    db_credentials = db_credentials.one_or_none()
    if db_credentials:
        is_verified, new_hash = verify_password(
            credentials.password,
            db_credentials.password
        )
        if new_hash:
            query = update(models.User).where(
                models.User.username == credentials.username
            ).values(password=new_hash)
            await session.execute(query)
            await session.commit()
        if is_verified:
            return credentials
        raise unauthed_exc
    raise unauthed_exc
