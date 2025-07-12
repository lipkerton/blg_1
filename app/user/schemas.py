from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    user_id: int
    username: str
    email: EmailStr | None = None

    class Config:
       from_attributes = True


class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr | None = None
