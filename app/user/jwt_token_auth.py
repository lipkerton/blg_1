from typing import Annotated
from datetime import datetime, timezone, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.config import settings


security = HTTPBearer()

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_jwt_token(data: dict) -> str:
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


def token_check(
    credentials: Annotated[str, Depends(security)]
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid or expired token",
        headers={"WWW-authenticate": "Bearer"}
    )
    jwt_token = credentials.credentials
    payload = verify_jwt_token(jwt_token)
    if payload:
        return payload
    raise unauthed_exc
