from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def index():
    return {'data': 'blog list'}

@app.get('/about')
def about():
    return {'About' : 'Blog app'}

@app.get('/blog/{id}') #for dynami routing use /{} and need to accept this variable in the path operaton fuction

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

