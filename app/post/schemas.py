from pydantic import BaseModel


class PostCreateSchema(BaseModel):
    title: str
    content: str


class PostSchema(PostCreate):
    post_id: int
