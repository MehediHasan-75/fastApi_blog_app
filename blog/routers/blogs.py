from fastapi import APIRouter, status, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, database, models

router = APIRouter()

@router.post('/blog', status_code= status.HTTP_201_CREATED, tags = ['Blogs'])
def create(request: schemas.BlogBase, db: Session = Depends(database.get_db)):
    new_blog = models.Blog(title = request.title, body = request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@router.get('/blog', response_model= List[schemas.ShowBlog], tags = ['Blogs'])
# we will get list of blogs from here
def all(db: Session = Depends(database.get_db)):
    blogs = db.query(models.Blog).all()
    return blogs

@router.get('/blog/{id}', status_code = 200, response_model= schemas.ShowBlog, tags = ['Blogs'])

def show(id: int, response: Response, db: Session = Depends(database.get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Blog with the id {id} is not avaliable")
    return blog

@router.delete('/blog/{id}', status_code=status.HTTP_204_NO_CONTENT,tags = ['Blogs'])
def destory(id, db: Session = Depends(database.get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = f"Blog with id {id} not found")
    blog.delete(synchronize_session= False)
    db.commit()
    return "Done"

@router.put('/blog/{id}', status_code= status.HTTP_202_ACCEPTED, tags = ['Blogs'])
def update(id, request: schemas.Blog, db: Session = Depends(database.get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)

    if not blog.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = f"Blog with id {id} not found")
    blog.update(request.body)
    db.commit()
    return "Updated successfully"