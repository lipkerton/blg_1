from fastapi import APIRouter
from sqlalchemy import select
# from sqlalchemy.sql import text

from .schemas import PostCreateSchema, PostGetSchema
from ..database import database, models


router = APIRouter()


@router.get("/p", response_model=list[PostGetSchema])
async def get_posts(session: database.SessionDep):
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
async def get_post(index: int, session: database.SessionDep):
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
async def add_post(post: PostCreateSchema, session: database.SessionDep):
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id
    )
    session.add(new_post)
    await session.commit()

