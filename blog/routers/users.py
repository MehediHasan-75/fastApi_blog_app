from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from ..hashing import Hash
from .. import database, models, schemas

router = APIRouter()
@router.post('/user', response_model= schemas.ShowUser, tags = ['Users'])
def create_user(request: schemas.User, db: Session = Depends(database.get_db)):
    hashedPassword = Hash.get_password_hash(request.password)
    new_user = models.User(name=request.name, email=request.email, password=hashedPassword)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('/user/{id}', response_model=schemas.ShowUser, tags = ['Users'])
def get_user(id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"User with the id {id} is not available")
    return user