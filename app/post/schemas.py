from datetime import datetime

from pydantic import BaseModel, EmailStr


class PostGetSchema(BaseModel):
    post_id: int
    username: str
    email: EmailStr | None = None
    created_at: datetime
    title: str
    content: str

    class Config:
        from_attributes = True


class PostCreateSchema(BaseModel):
    user_id: int
    title: str
    content: str
    
