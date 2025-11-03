from fastapi import APIRouter, status, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, database, models

router = APIRouter(
    prefix="/blog",
    tags=['Blogs'],
)

@router.post('/', status_code= status.HTTP_201_CREATED)
def create(request: schemas.BlogBase, db: Session = Depends(database.get_db)):
    new_blog = models.Blog(title = request.title, body = request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@router.get('/', response_model= List[schemas.ShowBlog])
# we will get list of blogs from here
def all(db: Session = Depends(database.get_db)):
    blogs = db.query(models.Blog).all()
    return blogs

@router.get('/{id}', status_code = 200, response_model= schemas.ShowBlog)

def show(id: int, response: Response, db: Session = Depends(database.get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"Blog with the id {id} is not avaliable")
    return blog

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def destory(id, db: Session = Depends(database.get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = f"Blog with id {id} not found")
    blog.delete(synchronize_session= False)
    db.commit()
    return "Done"

@router.put('/{id}', status_code= status.HTTP_202_ACCEPTED)
def update(id, request: schemas.Blog, db: Session = Depends(database.get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)

    if not blog.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail = f"Blog with id {id} not found")
    blog.update(request.body)
    db.commit()
    return "Updated successfully"