import json
from collections import namedtuple

import pytest
import requests
from sqlalchemy import text

from .setup import password, token


endpoint = "/p"
Post = namedtuple("Post", ["title", "content", "user_id"])

User = namedtuple("User", ["username", "email", "password"])
user = User("steve", "stevevach@gmail.com", "123456")
user_json = json.dumps(user._asdict())


@pytest.fixture(scope="module", autouse=True)
def make_user(socket):
    
    endpoint_user = "/user"
    endpoint_login = "/login"

    response = requests.post(
       f"{socket}{endpoint_user}",
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
    assert response.status_code == 200, create_error_user_message
    
    basic_auth = requests.auth.HTTPBasicAuth(user.username, user.password)
    response = requests.post(
        f"{socket}{endpoint_login}",
        auth=basic_auth
    )
    message_entry_user_error = (
        "Не удалось выполнить вход пользователем."
        f"username: {user.username}"
        f"email: {user.email}"
        f"password: {user.password}"
        f"response: {response.status_code}"
    )
    assert response.status_code == 200, message_entry_user_error
    token._token = response.json()

    yield

    response = requests.delete(
        f"{socket}{endpoint}",
        headers={"Authorization": token.token}
    )
    message_delete_user_error = (
        "Не удалось удалить пользователя."
        f"username: {user.username}"
        f"email: {user.email}"
        f"password: {user.password}"
        f"response: {response.status_code}"
    )
    assert response.status_code == 200, message_delete_user_error


class TestPost:
    
    @pytest.fixture(scope="class")
    async def post(session):
        query = f"""
            select user_id
            from users
            where 
                username = {user.username}
                and email = {user.email}
        """
        result = await session.execute(text(query))
        result = result.one()
        user_id = result.get("user_id", None)
        message_get_user_id_error = (
            "Не удалось получить идентификатор пользователя."
            f"username: {user.username}"
            f"email: {user.email}"
            f"password: {user.password}"
            f"query: {query}"
        )
        assert user_id, get_user_id_error
        
        yield Post("Тестовый пост (заголовок)", "Тело тестового поста", user_id)

    async def test_add_post(socket, post):
        post_json = json.dumps(post._asdict())
        response = requests.post(
            f"{socket}{endpoint}"
            headers={
                "Authorization": token.token,
                "Content-Type": "application/json"
            },
            data=post_json
        )
        message_add_post_error = (
            "Не удалось добавить пост.\n"
            "Status code: {response.status_code}"
        )
        assert response.status_code == 200, message_add_post_error
