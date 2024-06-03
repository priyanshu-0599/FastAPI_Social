from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, Annotated


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    # id : int
    email: EmailStr
    # model_config = ConfigDict()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = False
    # rating: Optional[int] = None


class PostResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    published: bool = False
    # rating: Optional[int] = None
    user: UserResponse
    # model_config = ConfigDict()


class PostVoteOut(BaseModel):
    Post: PostResponse
    votes: int


class Token(BaseModel):
    access_token: str
    token_type: str
    # model_config = ConfigDict()


class TokenData(BaseModel):
    id: int | str
    timestamp: str


class Votes(BaseModel):
    post_id: int
    dir: Annotated[int, Field(strict=True, ge=0, le=1)]
