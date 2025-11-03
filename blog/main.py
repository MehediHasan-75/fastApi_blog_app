from pyexpat import model
from typing import List
from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import schema
from . import schemas, models
from .database import SessionLocal, engine
from sqlalchemy.orm import Session 
from .hashing import Hash
app = FastAPI()

models.Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/blog', status_code= status.HTTP_201_CREATED, tags = ['Blogs'])
def create(request: schemas.BlogBase, db: Session = Depends(get_db)):
    new_blog = models.Blog(title = request.title, body = request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@app.get('/blog', response_model= List[schemas.ShowBlog], tags = ['Blogs'])
# we will get list of blogs from here
def all(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs

@app.get('/blog/{id}', status_code = 200, response_model= schemas.ShowBlog, tags = ['Blogs'])

def show(id: int, response: Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Blog with the id {id} is not avaliable")
    return blog

@app.delete('/blog/{id}', status_code=status.HTTP_204_NO_CONTENT,tags = ['Blogs'])
def destory(id, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = f"Blog with id {id} not found")
    blog.delete(synchronize_session= False)
    db.commit()
    return "Done"

@app.put('/blog/{id}', status_code= status.HTTP_202_ACCEPTED, tags = ['Blogs'])
def update(id, request: schemas.Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)

    if not blog.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = f"Blog with id {id} not found")
    blog.update(request.body)
    db.commit()
    return "Updated successfully"

@app.post('/user', response_model= schemas.ShowUser, tags = ['Users'])
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    hashedPassword = Hash.get_password_hash(request.password)
    new_user = models.User(name=request.name, email=request.email, password=hashedPassword)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get('/user/{id}', response_model=schemas.ShowUser, tags = ['Users'])
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"User with the id {id} is not available")
    return user