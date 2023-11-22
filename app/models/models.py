from typing import Annotated, Union
from annotated_types import Le
from pydantic import BaseModel, EmailStr, PositiveInt


class User(BaseModel):
    name: str
    age: int
    is_adult: bool = False


class Identification(BaseModel):
    login: str
    email: str
    password: str


class Feedback(BaseModel):
    name: str
    message: str


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Annotated[PositiveInt, None, Le(150)] = None
    is_subscribed: Union[bool, None]




