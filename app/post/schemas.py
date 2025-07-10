from datetime import datetime

from pydantic import BaseModel


class PostSchema(BaseModel):
    post_id: int
    user_id: int
    created_at: datetime
    title: str
    content: str

    class Config:
        from_attributes = True


class PostCreateSchema(BaseModel):
    user_id: int
    title: str
    content: str
