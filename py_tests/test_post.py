import json
from collections import namedtuple

import pytest
import requests
from sqlalchemy import text

from .conftest import password, token


endpoint = "/p"
Post = namedtuple("Post", ["user_id", "title", "content"])

User = namedtuple("User", ["username", "email", "password"])
user = User("steve", "stevevach@gmail.com", "123456")
user_json = json.dumps(user._asdict())

error_user_message_info = (
    f"username: {user.username}\n"
    f"email: {user.email}\n"
    f"password: {user.password}\n"
    "response: {response.status_code}\n"
)

@pytest.fixture(scope="module", autouse=True)
def make_user():
    
    endpoint_user = "/user"
    endpoint_login = "/login"

    socket = f"http://127.0.0.1:8000"

    response = requests.post(
       f"{socket}{endpoint_user}",
       headers={"Content-Type": "application/json"},
       data=user_json
    )
    assert response.status_code == 200, (
        "Не удалось создать пользователя.\n",
        error_user_message_info.format(response.status_code)
    )
    basic_auth = requests.auth.HTTPBasicAuth(user.username, user.password)
    response = requests.post(
        f"{socket}{endpoint_login}",
        auth=basic_auth
    )
    assert response.status_code == 200, (
        "Не удалось выполнить вход пользователем.\n",
        error_user_message_info.format(response.status_code)
    )

    token._token = response.json()

    yield
    
    username_path_param = f"/{user.username}"
    response = requests.delete(
        f"{socket}{endpoint_user}{username_path_param}",
        headers={"Authorization": token.token}
    )
    assert response.status_code == 200, (
        "Не удалось удалить пользователя.\n",
        error_user_message_info.format(response.status_code)
    )


class TestPost:

    error_post_message_info = (
        "Status code: {reponse.status_code}"
    )

    @pytest.fixture
    async def post(cls, session):
        query = f"""
            select user_id
            from users
            where 
                username = '{user.username}'
                and email = '{user.email}'
        """
        result = await session.execute(text(query))
        user_id, *_ = result.one()
        assert user_id, (
            "Не удалось получить идентификатор пользователя.\n",
            error_user_message_info.format(None)
        )
        yield Post(
            user_id,
            "Мой первый пост!",
            "Содержимое моего первого поста."
        )   

    async def test_add_post(cls, socket, post):
        post_json = json.dumps(post._asdict())
        response = requests.post(
            f"{socket}{endpoint}",
            headers={
                "Authorization": token.token,
                "Content-Type": "application/json"
            },
            data=post_json
        )
        assert response.status_code == 200, (
            "Не удалось добавить пост.\n",
            error_post_message_info.format(response.status_code)
        )
