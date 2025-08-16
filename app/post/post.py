"""
Методы и эндпоинты, которые связаны с юзерами.
Сделано:
1) Метод для создания поста.
3) Метод для получения списка постов.
4) Метод для получения конкретного поста.
5) Метод для удаления поста.
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select, delete

from .schemas import PostCreateSchema, PostGetSchema
from ..database import database, models
from ..user.jwt_token_auth import token_check


router = APIRouter()

CredentialsToken = Annotated[dict, Depends(token_check)]


@router.get("/p", response_model=list[PostGetSchema])
async def get_posts(
    session: database.SessionDep,
):
    """
    Через SELECT получаем все посты.
    """
    query = select(
        models.Post.post_id,
        models.User.username,
        models.User.email,
        models.Post.created_at,
        models.Post.title,
        models.Post.content
    )
    query = query.join(models.User, models.Post.user_id == models.User.user_id)
    result = await session.execute(query)
    return result.all()


@router.get("/p/{index:int}", response_model=PostGetSchema)
async def get_post(
    index: int,
    session: database.SessionDep
):
    """
    Через SELECT получаем конкретный пост
    с идентификатором `index`.
    """
    query = select(
        models.Post.post_id,
        models.User.username,
        models.User.email,
        models.Post.created_at,
        models.Post.title,
        models.Post.content
    )
    query = query.join(models.User, models.Post.user_id == models.User.user_id)
    query = query.where(models.Post.post_id == index)
    result = await session.execute(query)
    return result.one()


@router.post("/p")
async def add_post(
    post: PostCreateSchema,
    session: database.SessionDep,
    user: CredentialsToken
):
    """
    Добавляем новый пост в БД.
    """
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=user.user_id  # type: ignore
    )
    session.add(new_post)
    await session.commit()


@router.delete("/p/{index:int}")
async def delete_post(
    index: int,
    session: database.SessionDep,
    user: CredentialsToken
):
    """
    Удаляем пост с идентификатором
    из параметра пути.
    Но только если такой пост был написан
    пользователем, который отправил запрос на
    удаление.
    """
    query = delete(models.Post).where(
        models.Post.post_id == index,
        models.Post.user_id == user.user_id  # type: ignore
    )
    await session.execute(query)
    await session.commit()
