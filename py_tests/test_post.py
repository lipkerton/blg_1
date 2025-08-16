"""
Тесты для проверки работы постов.
1) Проверка на добавление поста.
"""
import json
from collections import namedtuple

import pytest
import requests

from .conftest import (
    token, socket, TIMEOUT
)


ENDPOINT = "/p"
Post = namedtuple("Post", ["title", "content"])
post = Post("Мой первый пост!", "Содержимое моего первого поста!")
post_json = json.dumps(post._asdict())

User = namedtuple("User", ["username", "email", "password"])
user = User("steve", "stevevach@gmail.com", "123456")
user_json = json.dumps(user._asdict())

ERROR_USER_MESSAGE_INFO = (
    f"username: {user.username}\n"
    f"email: {user.email}\n"
    f"password: {user.password}\n"
    "response: {status_code}\n"
)
ERROR_POST_MESSAGE_INFO = (
    "Status code: {status_code}"
)

@pytest.fixture(scope="module", autouse=True)
def make_user():
    """
    Делаем перед началом тестирование юзера,
    а потом его удаляем.
    Юзер нужен для создания и работы с постами.
    """
    endpoint_user = "/user"
    endpoint_login = "/login"

    response = requests.post(
       f"{socket.socket}{endpoint_user}",
       headers={"Content-Type": "application/json"},
       data=user_json,
       timeout=TIMEOUT
    )
    assert response.status_code == 200, (
        "Не удалось создать пользователя.\n" + \
        ERROR_USER_MESSAGE_INFO.format(
            status_code=response.status_code
        )
    )
    response = requests.post(
        f"{socket.socket}{endpoint_login}",
        auth=(user.username, user.password),
        timeout=TIMEOUT
    )
    assert response.status_code == 200, (
        "Не удалось выполнить вход пользователем.\n" + \
        ERROR_USER_MESSAGE_INFO.format(
            status_code=response.status_code
        )
    )

    token.token = response.json()

    yield

    username_path_param = f"/{user.username}"
    response = requests.delete(
        f"{socket.socket}{endpoint_user}{username_path_param}",
        headers={"Authorization": token.token},
        timeout=TIMEOUT
    )
    assert response.status_code == 200, (
        "Не удалось удалить пользователя.\n" + \
        ERROR_USER_MESSAGE_INFO.format(
            status_code=response.status_code
        )
    )


class TestPost:
    """
    Я сделал класс для тестов, чтобы разделить
    сами тесты для постов и подготовку в виде фиксуры
    для создания пользователя.
    Еще я хотел попробовать использовать классы в тестах.
    """
    async def test_add_post(self):
        """
        Проверяем, что метод на добавление поста в БД
        возвращает нужный статус код.
        """
        response = requests.post(
            f"{socket.socket}{ENDPOINT}",
            headers={
                "Authorization": token.token,
                "Content-Type": "application/json"
            },
            data=post_json,
            timeout=TIMEOUT
        )
        assert response.status_code == 200, (
            "Не удалось добавить пост.\n",
            ERROR_POST_MESSAGE_INFO.format(
                status_code=response.status_code
            )
        )
