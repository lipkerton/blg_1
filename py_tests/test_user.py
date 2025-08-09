import json
from collections import namedtuple

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.exc import NoResultFound
import requests
from requests.auth import HTTPBasicAuth

from .setup import password, token
from ..app.user import schemas


pytestmark = pytest.mark.user

endpoint = "/user"
User = namedtuple("User", ["username", "password", "email"])
user = User("steve", "123456", "stevevach@gmail.com")

user_json = json.dumps(user._asdict())


@pytest.fixture(scope="function")
async def db_user(session):
    query = f"""
        select username, password, email from users
        where
            username = '{user.username}'
            and email = '{user.email}';
    """
    result = await session.execute(text(query))
    return result


def test_create_user(socket):
    response = requests.post(
        f"{socket}{endpoint}",
        headers={"Content-Type": "application/json"},
        data=user_json
    )
    assert response.status_code == 200


def test_check_new_user_db(db_user):
    hashed_password = password.get_password_hash(user.password)

    try:
        db_user = User._make(db_user.one())
    except TypeError as error:
        raise f"""
            Запрос к БД по параметрам {user.username}, {user.email}
            не удался: вернулся неполный результат.
            {error}.
        """
    except NoResultFound as error:
        raise f"""
            Запрос к БД по параметрам {user.username}, {user.email}
            не удался: вернулся пустой результат.
            {error}.
        """

    assert db_user.username == user.username, \
        f"""Не совпадает имя пользовтаеля.
        db_username: {db_user.username},
        init_username: {user.username}."""
    assert password.verify_password(user.password, db_user.password), \
        f"""Не сопадают пароли.
        db_password: {db_user.password},
        init_password: {hashed_password}."""
    assert db_user.email == user.email, \
        f"""Не совпадают адреса эл.почты.
        db_email: {db_user.email},
        init_email: {user.email}."""


def test_login(socket):
    endpoint = "/login"
    basic_auth = HTTPBasicAuth(user.username, user.password)
    response = requests.post(
        f"{socket}{endpoint}",
        auth=basic_auth
    )
    assert response.status_code == 200, \
        f"Логин не удался. Кредиты: {user.username}, {user.password}"
    token._token = response.json()


def test_get_users(socket):
    response = requests.get(
        f"{socket}{endpoint}",
        headers={"Authorization": token.token}
    )
    assert response.status_code == 200, \
        "Не удалось получить список пользователей."
    assert response.json(), \
        "Список пользователей пуст."


def test_get_user(socket):
    username_path_param = f"/{user.username}"
    response = requests.get(
        f"{socket}{endpoint}{username_path_param}",
        headers={"Authorization": token.token}
    )
    assert response.status_code == 200, \
        "Не удалось получить пользователя."
    result = response.json()
    assert result["username"] == user.username, \
        f"""Имя пользователя не совпадает.
        result_username: {result['username']},
        user_username: {user.username}."""
    assert result["email"] == user.email, \
        f"""Почта пользователя не совпадает.
        result_email: {result['email']},
        user_username: {user.email}."""


def test_del_user(socket):
    username_path_param = f"/{user.username}"
    response = requests.delete(
        f"{socket}{endpoint}{username_path_param}",
        headers={"Authorization": token.token}
    )
    assert response.status_code == 200, \
        "Не удалось удалить пользователя."


def test_check_deleted_user_db(db_user):

    try:
        db_user.one()
    except NoResultFound:
        pass
    else:
        raise AssertionError(
            f"""После удаления данные пользователя в БД:
            {db_user}."""
        )
