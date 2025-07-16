from pydantic import BaseModel, EmailStr


class UserGetSchema(BaseModel):
    user_id: int
    username: str
    email: EmailStr | None = None

    class Config:
       from_attributes = True


class UserCreateSchema(BaseModel):
    username: str
    password: str
    email: EmailStr | None = None
