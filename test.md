# Response model = Pydantic schema for response

-> for the response we are also going to define models. for that add `response_model=schemas.ShowBlog` in the decorator.

-> Why this needed?

* When we want to show a specific part of data to user. The fields we assign here are the only ones the client will see. Here we are not showing the `blog id` created for each blog.
* normal response

```json
{
  "id": 2,
  "title": "xyz title",
  "body": "this is the sample body"
}
```

* with Pydantic response schema

```json
{
  "title": "xyz title",
  "body": "this is the sample body"
}
```

* how to do this?
* first go to `schemas.py`
  and add

```python
from pydantic import BaseModel

class Blog(BaseModel):
    title: str
    body: str

class ShowBlog(Blog):
    class Config:
        orm_mode = True
```

* this will use our previously created `Blog`.  we want `title` and `body` which are already defined in `Blog`.

* now go to `main.py` and set the `response_model` as `schemas.ShowBlog`

```python
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import schemas, models
from .database import engine, SessionLocal

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/blog/{id}', status_code=status.HTTP_200_OK, response_model=schemas.ShowBlog)
def show(id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with id {id} not found"
        )
    return blog
```

* but if we use this with `/blog` which is returning a list of blogs, we will get internal server error if we don’t specify a list response.
* solution = define the output type as a list of this schema.

```python
from typing import List

@app.get('/blog', response_model=List[schemas.ShowBlog])
def all(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs
```

* you can read this in the FastAPI docs response model section.

---

# Create user

* create user schema in `schemas.py`

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    password: str

class ShowUser(BaseModel):
    name: str
    email: str

    class Config:
        orm_mode = True
```

* use it from `main.py`

```python
from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session
from . import schemas, models
from .database import engine, SessionLocal

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/user', response_model=schemas.ShowUser)
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    # will implement hashing below
    ...
```

* we need to save it in db. so we need database; before that create a SQLAlchemy model.

```python
# models.py (add)
from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
```

* but password is not hashed. go to FastAPI docs and research password hashing.

`pip install passlib[bcrypt]`

* create `hashing.py` and create hash helpers.

```python
# hashing.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash:
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
```

* to show a user we don’t want to show password so what we need?
* yes we need to create a response schema (already added `ShowUser`).

```python
@app.post('/user', response_model=schemas.ShowUser)
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    from .hashing import Hash
    hashed_password = Hash.get_password_hash(request.password)
    new_user = models.User(name=request.name, email=request.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
```

---

# upgrading docs.

* in docs currently all the routes are actually set as default.
* solution = use docs tags → see metadata and docs from FastAPI and use your tags

`@app.get('/user', tags=['Users'])`

---

# Relationships

* every blog is related to a user
* in FastAPI/SQLAlchemy docs, search relationships and see.

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Blog(Base):
    __tablename__ = 'blogs'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    creator = relationship("User", back_populates="blogs")


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    blogs = relationship("Blog", back_populates="creator")
```

--> shortly describe main lines. gpt ok?

* edit response model for showing owner

```python
from typing import Optional
from pydantic import BaseModel

class BlogBase(BaseModel):
    title: str
    body: str

class ShowUser(BaseModel):
    name: str
    email: str
    class Config:
        orm_mode = True

class ShowBlog(BlogBase):
    creator: Optional[ShowUser]
    class Config:
        orm_mode = True
```

--> add some explanation

* `orm_mode = True` allows Pydantic to read SQLAlchemy model objects directly.

---

# How to refactor API routes?

* FastAPI user guide → bigger applications / multiple files.

* create `routers` folder → create `__init__.py` → create two separate files `blogs.py` and `users.py`

* for each dedicated file import `APIRouter` and create an instance of a router.

* gradually move every related route here

* move the `get_db` function into `database.py`.

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = 'sqlite:///./blog.db' 
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

-- include routers in main app.

```python
from fastapi import FastAPI
from . import models
from .database import engine
from .routers import blogs, users

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(blogs.router)
app.include_router(users.router)
```

# API routers options

* common prefix of all routes under a router and tags can be moved into:

```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/blog",
    tags=['Blogs'],
)
```

# now we have database operations in router. but think about this! routers are only for path and sending response

* so, do other things in separate space.

* create a repository and make changes. after that

// `main.py` (already shown above)

// routers
// `blogs.py`

```python
from fastapi import APIRouter, status, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, database, models
from ..repository import blogs as blog_repo

router = APIRouter(
    prefix="/blog",
    tags=['Blogs'],
)

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.ShowBlog)
def create(request: schemas.BlogBase, db: Session = Depends(database.get_db)):
    return blog_repo.create(request, db)

@router.get('/', response_model=List[schemas.ShowBlog])
def all(db: Session = Depends(database.get_db)):
    return blog_repo.all(db)

@router.get('/{id}/', status_code=200, response_model=schemas.ShowBlog)
def show(id: int, db: Session = Depends(database.get_db)):
    return blog_repo.show(id, db)

@router.delete('/{id}/', status_code=status.HTTP_204_NO_CONTENT)
def destroy(id: int, db: Session = Depends(database.get_db)):
    return blog_repo.destroy(id, db)

@router.put('/{id}/', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.ShowBlog)
def update(id: int, request: schemas.BlogBase, db: Session = Depends(database.get_db)):
    return blog_repo.update(id, request, db)
```

// `users.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, schemas
from ..repository import users as user_repo

router = APIRouter(
    prefix="/user",
    tags=['Users'],
)

@router.post('/', response_model=schemas.ShowUser)
def create_user(request: schemas.User, db: Session = Depends(database.get_db)):
    return user_repo.create_user(request, db)

@router.get('/{id}/', response_model=schemas.ShowUser)
def get_user(id: int, db: Session = Depends(database.get_db)):
    return user_repo.get_user(id, db)
```

// repository
// `blogs.py`

```python
from .. import schemas, models
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

def create(request: schemas.BlogBase, db: Session):
    new_blog = models.Blog(title=request.title, body=request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

def all(db: Session):
    return db.query(models.Blog).all()

def show(id: int, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with the id {id} is not available")
    return blog

def destroy(id: int, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with id {id} not found")
    blog.delete(synchronize_session=False)
    db.commit()
    return "Done"

def update(id: int, request: schemas.BlogBase, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with id {id} not found")
    blog.update(request.dict())
    db.commit()
    return db.query(models.Blog).filter(models.Blog.id == id).first()
```

// `users.py`

```python
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..hashing import Hash
from .. import models, schemas

def create_user(request: schemas.User, db: Session):
    hashed_password = Hash.get_password_hash(request.password)
    new_user = models.User(name=request.name, email=request.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user(id: int, db: Session):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"User with the id {id} is not available")
    return user
```

--> here is all previous code. use anywhere needed:

```python
from fastapi import FastAPI
from . import models
from .database import engine
from .routers import blogs, users

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(blogs.router)
app.include_router(users.router)
```

# moved to database file

```python
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
```

# moved to routers (examples previously in main.py)

```python
# create, all, show, destroy, update routes moved to routers/blogs.py
# create_user, get_user routes moved to routers/users.py
```
