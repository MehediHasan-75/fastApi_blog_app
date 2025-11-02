from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

@app.get('/')
def index():
    return {'data': 'base directory'}

@app.get('/about')
def about():
    return {'About' : 'Blog app'}

@app.get('/blog')
def index(limit: int, published: bool, sort: Optional[str] = None):
    if published:
        return {'data': f'blog list {published} blogs form the bd'}
    else:
        return {'data': 'all the blogs form db'}

@app.get('/blog/{id}') 

def show(id : int):
    #TODO: return blog with id = id

    return {'data': id}


@app.get('/blog/{id}/comments')

def comments(id: int):
    #return comments of blog with id = id
    return {'data': {'Comment1', 'Comment2'}}


@app.get('/blog/unpublished')
def unpublished():
    # return unpublished blog
    return {'data': 'all unpublished blogs'}


class Blog(BaseModel):
    title: str
    body: str
    publised: Optional[bool]

@app.post('/blog')
def create_blog(request: Blog):
    return {'data': f"Blog is created wiht {request.title}"}  

