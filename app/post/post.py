from fastapi import APIRouter
from sqlalchemy.sql import text

from .schemas import PostCreateSchema, PostSchema
from ..database import database, models


router = APIRouter()


@router.get("/p", response_model=list[PostSchema])
async def get_posts(session: database.SessionDep):
    result = await session.execute(text("""
        select post_id, title, content
        from post
    """))
    return result.all()


@router.post("/p")
async def add_post(post: PostCreateSchema, session: database.SessionDep):
    new_post = models.Post(
        title=post.title,
        content=post.content
    )
    session.add(new_post)
    await session.commit()

