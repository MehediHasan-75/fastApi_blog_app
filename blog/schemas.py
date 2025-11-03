from pydantic import BaseModel
from typing import List, Optional

class BlogBase(BaseModel):
    title: str
    body: str

class Blog(BlogBase):
    class Config:
        orm_mode = True


class ShowUser(BaseModel):
    name: str
    email: str
    blogs: List['ShowBlog'] = []  

    class Config:
        orm_mode = True


class ShowBlog(BlogBase):
    creator: Optional[ShowUser]  
    class Config:
        orm_mode = True


class User(BaseModel):
    name: str
    email: str
    password: str
