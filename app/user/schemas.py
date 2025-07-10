from pydantic import BaseModel


class UserSchema(BaseModel):
    user_id: int
    username: str

    class Config:
       from_attributes = True


class UserCreateSchema(BaseModel):
    username: str
