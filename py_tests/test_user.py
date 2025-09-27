"""
Тесты для проверки работы всего, что касается юзеров.
Реализовано:
1) Проверка добавления пользователя (+ проверка добавления в БД).
2) Проверка логина.
3) Проверка корректной работы эндопинтов на
получение пользователя/списка пользователей.
4) Проверка корректного удаления пользователя.
5) Проверка прав доступа анонимного пользователя.
"""
import json
from collections import namedtuple

import pytest
import requests
from sqlalchemy import text
from sqlalchemy.exc import NoResultFound

from .conftest import TIMEOUT, password, token, socket


pytestmark = pytest.mark.user

ENDPOINT = "/user"
User = namedtuple("User", ["username", "password", "email"])
user = User("steve", "123456", "stevevach@gmail.com")
user_json = json.dumps(user._asdict())

ERROR_USER_MESSAGE_INFO = (
    f"username: {user.username}\n"
    f"email: {user.email}\n"
    f"password: {user.password}\n"
    "response: {status_code}"
)

@pytest.fixture(name="db_user")
async def get_db_user(session):
    """
    Фиксура должна отдавать пользователя из БД.
    """
    query = f"""
        select username, password, email from users
        where
            username = '{user.username}'
            and email = '{user.email}';
    """
    result = await session.execute(text(query))
    yield result


def test_create_user():
    """
    Тест высылает POST-запрос на эндпоинт
    `/user` с данными для создания пользователя.
    """
    response = requests.post(
        f"{socket.socket}{ENDPOINT}",
        headers={"Content-Type": "application/json"},
        data=user_json,
        timeout=TIMEOUT
    )
    assert response.status_code == 200, (
        "Не удалось создать пользователя.\n" + \
        ERROR_USER_MESSAGE_INFO.format(status_code=response.status_code)
    )


def test_check_new_user_db(db_user):
    """
    Проверяем наличие созданного пользователя в БД.
    """
    hashed_password = password.get_password_hash(user.password)

    try:
        db_user = User._make(db_user.one())
    except TypeError as error:
        raise TypeError(
            "Запрос не удался: вернулся неполный результат.\n" + \
            ERROR_USER_MESSAGE_INFO.format(
                status_code="Это был прямой запрос в БД."
            )
        ) from error
    except NoResultFound as error:
        raise NoResultFound(
            "Запрос не удался: вернулся пустой результат.\n" + \
            ERROR_USER_MESSAGE_INFO.format(
                status_code="Это был прямой запрос в БД."
            )
        ) from error
    assert db_user.username == user.username, (
        "Не совпадает имя пользовтаеля.\n",
        f"db_username: {db_user.username}\n",
        f"init_username: {user.username}"
    )
    assert password.verify_password(user.password, db_user.password), (
        "Не совпадают пароли.\n",
        f"db_password: {db_user.password}\n",
        f"init_password: {hashed_password}"
    )
    assert db_user.email == user.email, (
        "Не совпадают эл.почты.\n"
        f"db_password: {db_user.password}\n"
        f"init_password: {hashed_password}"
    )

def test_login():
    """
    Тест высылает POST-запрос на эндпоинт
    `/login` с логином-паролем для входа.
    """
    endpoint = "/login"
    response = requests.post(
        f"{socket.socket}{endpoint}",
        auth=(user.username, user.password),
        timeout=TIMEOUT
    )
    assert response.status_code == 200, (
        "Логин не удался.\n"
        f"Кредиты: {user.username}, {user.password}"
    )
    token.token = response.json()


def test_get_users():
    """
    Тест высылает GET-запрос на эндпоинт
    `/user`, чтобы получить список пользователей.
    Это защищенный эндпоинт, поэтому к запросу
    добавляем токен, полученный на логине.
    """
    response = requests.get(
        f"{socket.socket}{ENDPOINT}",
        headers={"Authorization": token.token},
        timeout=TIMEOUT
    )
    assert response.status_code == 200, \
        "Не удалось получить список пользователей."
    assert response.json(), \
        "Список пользователей пуст."


def test_get_user():
    """
    Тест высылает GET-запрос на эндпоинт
    `/user`, чтобы получить пользователя.
    Это защищенный эндпоинт, поэтому к запросу
    добавляем токен, полученный на логине.
    """
    username_path_param = f"/{user.username}"
    response = requests.get(
        f"{socket.socket}{ENDPOINT}{username_path_param}",
        headers={"Authorization": token.token},
        timeout=TIMEOUT
    )
    assert response.status_code == 200, \
        "Не удалось получить пользователя."
    result = response.json()
    assert result["username"] == user.username, (
        f"Имя пользователя не совпадает.\n"
        f"result_username: {result['username']}\n"
        f"user_username: {user.username}"
    )
    assert result["email"] == user.email, (
        f"Почта пользователя не совпадает.\n"
        f"result_email: {result['email']}\n"
        f"user_username: {user.email}"
    )


def test_anon_get_users():
    """
    Провека доступа анонима (без токена) к GET `/user`.
    """
    response = requests.get(
        f"{socket.socket}{ENDPOINT}",
        timeout=TIMEOUT
    )
    assert response.status_code == 403, (
        f"Аноним не должен получать доступ к {socket.socket}{ENDPOINT}.\n"
        "HTTP-метод: GET."
    )


def test_anon_get_user():
    """
    Проверка доступ анонима (без токена) к GET `/user/{username}`.
    """
    username_path_param = f"/{user.username}"
    response = requests.get(
        f"{socket.socket}{ENDPOINT}{username_path_param}",
        timeout=TIMEOUT
    )
    assert response.status_code == 403, (
        f"Аноним не должен получать доступ к {socket.socket}{ENDPOINT}.\n"
        "HTTP-метод: GET."
    )


def test_anon_delete_user():
    """
    Проверка доступ анонима (без токена) к DELETE `/user/{username}`.
    """
    response = requests.delete(
        f"{socket.socket}{ENDPOINT}",
        timeout=TIMEOUT
    )
    assert response.status_code == 403, (
        f"Аноним не должен получать доступ к {socket.socket}{ENDPOINT}.\n"
        "HTTP-метод: DELETE."
    )

def test_del_user():
    """
    Тест высылает DELETE-запрос на эндпоинт
    `/user`, чтобы удалить пользователя.
    Это защищенный эндпоинт, поэтому к запросу
    добавляем токен, полученный на логине.
    """
    response = requests.delete(
        f"{socket.socket}{ENDPOINT}",
        headers={"Authorization": token.token},
        timeout=TIMEOUT
    )


    assert response.status_code == 200, (
        "Не удалось удалить пользователя.\n" + \
        ERROR_USER_MESSAGE_INFO.format(status_code=response.response_code)
    )


def test_check_deleted_user_db(db_user):
    """
    Проверяем, что пользователь удалился из БД.
    """
    try:
        db_user.one()
    except NoResultFound:
        pass
    else:
        raise AssertionError(
            f"После удаления данные пользователя в БД: {db_user}."
        )
