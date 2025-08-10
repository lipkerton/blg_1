from collections import namedtuple

import pytest
import requests

from sqlalchemy import text


User = ("User", ["username", "email", "password", "static_token"])
Post = ("Post", ["title", "content", "user_id"])

user = User("steve", "stevevach@gmail.com", "123456", "1a")

@pytest.fixture(scope="module", autouse=True)
async def make_user(session):
    query = f"""
        insert into users(username, email, password, static_token)
        values (
            {user.username},
            {user.email},
            {user.password},
            {user.static_token}
        )
    """
    await session.execute(query)
    yield
    query = f"""
        delete from users
        where
            username = {user.username}
            and email = {user.email}
            and password = {user.password}
            and static_token = {user.static_token}
    """
    await session.execute(query)


@pytest.fixture(scope="module", autouse=True)
async def get_user(session):
    query = f"""
        select user_id from users
        where username = {user.username}
    """
    result = await session.execute(query)
    user = result.one()
    yield user["user_id"]


@pytest.fixture
async def make_post_obj(session, user):
    post
