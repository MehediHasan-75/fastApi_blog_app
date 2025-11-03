from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, schemas
from ..repository import users

router = APIRouter(
    prefix="/user",
    tags=['Users'],
)
@router.post('/', response_model= schemas.ShowUser, tags = ['Users'])
def create_user(request: schemas.User, db: Session = Depends(database.get_db)):
    return users.create_user(request, db)

@router.get('/{id}/', response_model=schemas.ShowUser, tags = ['Users'])
def get_user(id: int, db: Session = Depends(database.get_db)):
    return users.get_user(id, db)