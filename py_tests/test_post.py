from collections import namedtuple

import pytest
import requests
from sqlalchemy import text

from .setup import password, token


User = namedtuple(
    "User",
    ["username", "email", "password", "static_token"]
)
Post = (
    "Post",
    ["title", "content", "user_id"]
)

user = User(
    "steve",
    "stevevach@gmail.com",
    "123456",
    "1a"
)


class TestPost:

    @classmethod
    @pytest.fixture(scope="class", autouse=True)
    async def make_user(cls, session):
        
        hashed_password = password.get_hashed_password(
            user.password
        )

        query = f"""
            insert into users(
                username,
                email,
                password,
                static_token
            )
            values (
                {user.username},
                {user.email},
                {hashed_password},
                {user.static_token}
            )
            returning user_id;
        """
        result = await session.execute(query)
        result = result.one()
        cls.user_id = result["user_id"]
        yield
        query = f"""
            delete from users
            where
                username = {user.username}
                and email = {user.email}
                and password = {hashed_password}
                and static_token = {user.static_token}
        """
        await session.execute(query)
    
    @classmethod
    @pytest.fixture(scope="class", autouse=True)
    async def get_token(cls, socket):
        
        endpoint = "/login"
        basic_auth = HTTPBasicAuth(
            user.username, user.password
        )
        response = requests.post(
            f"{socket}{endpoint}",
            auth=basic_auth
        )
        assert response.status_code == 200, \
            f"""Логин не удался. Кредиты:
            {user.username}, {user.password}"""
        token._token = response.json()



