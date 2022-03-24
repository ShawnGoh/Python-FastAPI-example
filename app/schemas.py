from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, conint

# making use of python's inheritance
# Pydantic model that is used to define the schema of a request or response
# This is different from the SQL model which is used for defining columns in the SQL database

# User Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserCreateResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode=True

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode=True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    id: Optional[str] = None

# ------------------------------------------------------------------------------------
# Posts Pydantic models
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True 

class PostCreate(PostBase):
    pass

class Response(PostBase):
    id: int
    created_at: datetime
    user_id: int
    owner: UserResponse
    class Config:
        orm_mode=True

class newPost(BaseModel):
    Post: Response
    votes: int

    class Config:
        orm_mode=True

# ------------------------------------------------------------------------------------
# Votes Pydantic models

class Vote(BaseModel):
    post_id: int
    vote_dir: conint(le=1)