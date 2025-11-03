from fastapi import APIRouter, status, Depends, Response, HTTPException
from sqlalchemy.orm import Session, session
from typing import List
from .. import schemas, database, models
from ..repository import blogs
import blog
router = APIRouter(
    prefix="/blog",
    tags=['Blogs'],
)

@router.post('/', status_code= status.HTTP_201_CREATED)
def create(request: schemas.BlogBase, db: Session = Depends(database.get_db)):
    return blogs.create(request, db)

@router.get('/', response_model= List[schemas.ShowBlog])
def all(db: Session = Depends(database.get_db)):
    return blogs.all(db)

@router.get('/{id}/', status_code = 200, response_model= schemas.ShowBlog)

def show(id: int, response: Response, db: Session = Depends(database.get_db)):
    return blogs.show(id, db)

@router.delete('/{id}/', status_code=status.HTTP_204_NO_CONTENT)
def destory(id, db: Session = Depends(database.get_db)):
    return blogs.destory(id, db)

@router.put('/{id}/', status_code= status.HTTP_202_ACCEPTED)
def update(id, request: schemas.Blog, db: Session = Depends(database.get_db)):
    return blogs.update(id, request, db)