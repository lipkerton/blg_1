"""
Тесты для проверки работы постов.
1) Проверка на добавление поста.
2) Проверка на чтение конкретного поста.
3) Проверка на удаление поста.
"""
import json
from collections import namedtuple

import pytest
import requests
from sqlalchemy import select

from ..app.database import models
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
    f"title: {post.title}\n"
    f"content: {post.content}\n"
    "response: {status_code}"
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

    response = requests.delete(
        f"{socket.socket}{endpoint_user}",
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
    @pytest.fixture(name="post_id")
    async def get_post_id(self, session):
        """
        Фиксура обращается к БД для извлечения post_id.
        """
        query = select(
            models.Post.post_id
        ).join(
            models.User, models.Post.user_id == models.User.user_id
        ).where(
            models.User.username == user.username,
            models.Post.content == post.content,
            models.Post.title == post.title
        )
        result = await session.execute(query)
        (post_id,) = result.one()
        return post_id

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
            "Не удалось добавить пост.\n" + \
            ERROR_POST_MESSAGE_INFO.format(
                status_code=response.status_code
            )
        )

    async def test_get_posts(self):
        """
        Проверяем, что метод на получение всех постов из БД
        возвращает нужный статус код.
        """
        response = requests.get(
            f"{socket.socket}{ENDPOINT}",
            timeout=TIMEOUT
        )
        assert response.status_code == 200, (
            "Не удалось получить посты.\n" + \
            ERROR_POST_MESSAGE_INFO.format(
                status_code=response.status_code
            )
        )

    async def test_get_post(self, post_id):
        """
        Проверяем, что метод на получение поста из БД
        возвращает нужный статус код.
        """
        response = requests.get(
            f"{socket.socket}{ENDPOINT}/{post_id}",
            timeout=TIMEOUT
        )
        assert response.status_code == 200, (
            "Не удалось получить пост.\n" + \
            ERROR_POST_MESSAGE_INFO.format(
                status_code=response.status_code
            )
        )
        response_content = json.loads(response.text)
        assert response_content["username"] == user.username, (
            "В ответе указан неверный юзернейм.\n"
            f"response username: {response_content['username']}\n"
            f"initial username: {user.username}\n" + \
            ERROR_POST_MESSAGE_INFO.format(
                status_code=response.status_code
            )
        )
        assert response_content["title"] == post.title, (
            "В ответе у поста неверный заголовок.\n"
            f"response title: {response_content['title']}"
            f"initial title: {post.title}\n" + \
            ERROR_POST_MESSAGE_INFO.format(
                status_code=response.status_code
            )
        )
        assert response_content["content"] == post.content, (
            "В ответе у поста неверное содержимое.\n"
            f"response content: {response_content['content']}"
            f"initial content: {post.content}\n" + \
            ERROR_POST_MESSAGE_INFO.format(
                status_code=response.status_code
            )
        )

    async def test_delete_post(self, post_id):
        """
        Проверяем, что метод на удаление поста из БД
        возвращает нужный статус-код.
        """
        response = requests.delete(
            f"{socket.socket}{ENDPOINT}/{post_id}",
            headers={
                "Authorization": token.token
            },
            timeout=TIMEOUT
        )
        assert response.status_code == 200, (
            f"Не удалось удалить пост {post_id}.\n" + \
            ERROR_POST_MESSAGE_INFO.format(
                status_code=response.status_code
            )
        )
