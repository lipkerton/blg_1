import json
from collections import namedtuple

import pytest
from sqlalchemy import text
from sqlalchemy.exc import NoResultFound
import requests
from requests.auth import HTTPBasicAuth

from .conftest import password, token
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
    yield result


def test_create_user(socket):
    response = requests.post(
        f"{socket}{endpoint}",
        headers={"Content-Type": "application/json"},
        data=user_json
    )
    message_create_user_error = (
        "Не удалось создать пользователя."
        f"username: {user.username}"
        f"email: {user.email}"
        f"password: {user.password}"
        f"response: {response.status_code}"
    )
    assert response.status_code == 200, message_create_user_error


def test_check_new_user_db(db_user):
    hashed_password = password.get_password_hash(user.password)

    message_not_found_user_error = (
        f"После создания пользователь {user.username}, {user.email}"
        "отсутствует в БД.\n{error}"
    )

    message_type_user_error = (
        f"Запрос к БД по параметрам {user.username}, {user.email}"
        "не удался: вернулся неполный результат.\n{error}"
    )
    message_no_result_user_error = (
        "Запрос к БД по параметрам {user.username}, {user.email}"
        "не удался: вернулся пустой результат.\n{error}"
    )
    message_username_user_error = (
        "Не совпадает имя пользовтаеля.\n"
        "db_username: {db_user.username}\n"
        f"init_username: {user.username}"
    )
    message_password_user_error = (
        "Не совпадают пароли.\n"
        "db_password: {db_user.password}\n"
        f"init_password: {hashed_password}"
    )
    message_email_user_error = (
        "Не совпадают адреса эл.почты.\n"
        "db_username: {db_user.email}\n"
        f"init_username: {user.email}"
    )

    try:
        db_user = User._make(db_user.one())
    except TypeError as error:
        raise message_type_user_error.format(error)  
    except NoResultFound as error:
        raise message_no_result_user_error.format(error)
    assert db_user.username == user.username, \
        message_username_user_error.format(db_user.username)
    assert password.verify_password(user.password, db_user.password), \
        message_password_user_error.format(db_user.password)
    assert db_user.email == user.email, \
        message_email_error.format(db_user.email)

def test_login(socket):
    endpoint = "/login"
    basic_auth = HTTPBasicAuth(user.username, user.password)
    response = requests.post(
        f"{socket}{endpoint}",
        auth=basic_auth
    )
    assert response.status_code == 200, \
        f"""Логин не удался. Кредиты:
        {user.username}, {user.password}"""
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


def test_anon_get_users(socket):
    response = requests.get(
        f"{socket}{endpoint}",
    )
    assert response.status_code == 403, \
        f"""Анонимный пользователь имеет доступ к
        списку всех пользователей: {socket}{endpoint}.
        HTTP-метод: GET."""


def test_anon_get_user(socket):
    username_path_param = f"/{user.username}"
    response = requests.get(
        f"{socket}{endpoint}{username_path_param}"
    )
    assert response.status_code == 403, \
        f"""Анонимный пользователь имеет доступ к 
        профилю зарегистрированного пользователя:
        {socket}{endpoint}{username_path_param}.
        HTTP-метод: GET."""


def test_anon_delete_user(socket):
    username_path_param = f"/{user.username}"
    response = requests.delete(
        f"{socket}{endpoint}{username_path_param}"
    )
    assert response.status_code == 403, \
        f"""Анонимный пользователь имеет доступ к 
        возможности удалить пользователя:
        {socket}{endpoint}{username_path_param}.
        HTTP-метод: DELETE."""


def test_del_user(socket):
    username_path_param = f"/{user.username}"
    response = requests.delete(
        f"{socket}{endpoint}{username_path_param}",
        headers={"Authorization": token.token}
    )

    message_delete_user_error = (
        "Не удалось удалить пользователя."
        f"username: {user.username}"
        f"email: {user.email}"
        f"password: {user.password}"
        f"response: {response.status_code}"
    )
    assert response.status_code == 200, \
        message_delete_user_error


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

