import json

import pytest
import pytest_asyncio
from sqlalchemy import text
import requests
from requests.auth import HTTPBasicAuth

from .setup import password, token
from ..app.user import schemas


endpoint = "/user"
user = {"username": "steve", "password": "123456", "email": "stevevach@gmail.com"} 
user_json = json.dumps(user)


def test_create_user(socket):
    response = requests.post(
        f"{socket}{endpoint}",
        headers={"Content-Type": "application/json"},
        data=user_json
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_check_new_user_db(session):
    hashed_password = password.get_password_hash(user["password"])
    query = f"""
        select username, password, email from users
        where
            username = '{user["username"]}'
            and email = '{user["email"]}';
    """
    result = await session.execute(text(query))
    db_username, db_password, db_email = result.one()
    assert result, "Данных нет в БД."
    assert db_username == user["username"], \
        f"""Не совпадает имя пользовтаеля.
        db_username: {db_username},
        init_username: {user["username"]}."""
    assert password.verify_password(user["password"], db_password), \
        f"""Не сопадают пароли.
        db_password: {db_password},
        init_password: {hashed_password}."""
    assert db_email == user["email"], \
        f"""Не совпадают адреса эл.почты.
        db_email: {db_email},
        init_email: {user["email"]}."""


@pytest.mark.asyncio
async def test_login(socket):
    endpoint = "/login"
    basic_auth = HTTPBasicAuth(user["username"], user["password"])
    response = requests.post(
        f"{socket}{endpoint}",
        auth=basic_auth
    )
    assert response.status_code == 200
    token._token = response.json()


@pytest.mark.asyncio
async def test_get_users(socket):
    response = requests.get(
        f"{socket}{endpoint}",
        headers={"Authorization": token.token}
    )
    assert response.status_code == 200

