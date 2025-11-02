# FastAPI doesn’t require you to use SQL (relational) databases. But you can use it via SQLAlchemy.

* SQLAlchemy is a Python SQL toolkit and Object Relational Mapper (ORM).
* Let’s understand this step by step by creating **CRUD** operations for the blog.

*(FastAPI is DB-agnostic; SQL examples commonly use SQLAlchemy/SQLModel.)* ([fastapi.tiangolo.com][1])

---

# Steps

* Create a new directory named `blog`. Inside this, create `__init__.py` to consider the folder as a Python module. *(So, what is a Python module? It’s a file or package that Python can import.)*
* Create a `main.py` inside `blog`

```python
# blog/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Blog(BaseModel):
    title: str
    body: str

@app.post('/blog')
def create(request: Blog):
    return request
```

* Run this using:

```
uvicorn blog.main:app --reload
```

* Create a `schemas.py` in the `blog` directory and move the Pydantic schema into it:

```python
# blog/schemas.py
from pydantic import BaseModel

class Blog(BaseModel):
    title: str
    body: str
```

* And change `main.py` to:

```python
# blog/main.py
from fastapi import FastAPI
from . import schemas

app = FastAPI()

@app.post('/blog')
def create(request: schemas.Blog):
    return request
```

*Request bodies in FastAPI are declared with Pydantic models.* ([fastapi.tiangolo.com][2])

---

# Now to create the DB connection (SQLAlchemy)

Go to the docs for SQLAlchemy ORM (e.g., the ORM Quick Start). ([docs.sqlalchemy.org][3])
*What is ORM?* Object-Relational Mapping maps your code objects to database tables (“relations”). For example, our class `Blog` can represent a SQL table `blogs` when we set `__tablename__ = 'blogs'`.

Create a file named `database.py` for creating our database.

**Traditional SQLAlchemy setup (SQLite example)**

```python
# blog/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = 'sqlite:///./blog.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite with threads
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
```

* The `connect_args={"check_same_thread": False}` pattern comes from the FastAPI SQL DB tutorial for SQLite. ([fastapi.tiangolo.com][1])
* Engines, Sessions, and Declarative base are core SQLAlchemy concepts. ([docs.sqlalchemy.org][4])

---

# NOW HOW TO CREATE MODEL

Inside the `blog` directory create `models.py` and follow the FastAPI/SQLAlchemy pattern again. We need to extend the model with `Base` declared in `database.py`.

```python
# blog/models.py
from sqlalchemy import Column, Integer, String
from .database import Base

class Blog(Base):
    __tablename__ = 'blogs'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    body = Column(String)
```

To view the DB, open `blog.db` with a SQLite client (e.g., TablePlus). Then connect to the DB file and you will see tables under the DB.

---

# We have created the model (tables) with database connection. Now how to use them?

Go to `main.py`:

```python
# blog/main.py
from fastapi import FastAPI
from . import models
from .database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
```

`models.Base.metadata.create_all(bind=engine)` will create tables if they don’t exist. It’s not a migrations tool; running it each start is harmless for creating missing tables but won’t alter existing schemas. ([docs.sqlalchemy.org][3])

---

# In summary

defining the path → creating the engine → creating session → creating the base → creating the model → model connected to table (Blog extends Base) → go to `main.py` → `models.Base.metadata.create_all(bind=engine)` → now get back to POST request and start storing.

---

# Now how to use this DB connection and where will it be used?

To use the database inside our create function, we need to receive a session in the path operation function where we want to use it.

**Dependency-injected DB session:**

```python
# blog/main.py (complete example)
from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session
from . import schemas, models
from .database import SessionLocal, engine

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# Dependency that yields a DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

* Using `Depends(get_db)` is the recommended way; when the request ends, the `finally` block closes the session. ([fastapi.tiangolo.com][5])

**Create blog (POST)**

```python
@app.post('/blog', status_code=status.HTTP_201_CREATED)
def create(request: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog
```

**Example body for `/blog`**

```json
{
  "title": "My First Blog",
  "body": "This is the content"
}
```

**Example response**

```json
{
  "id": 1,
  "title": "My First Blog",
  "body": "This is the content"
}
```

Summary: define the DB in the path operation function (`db: Session = Depends(get_db)`) → `Blog` table structure → `db.add(new_blog)` → `db.commit()` → `db.refresh(new_blog)` → return `new_blog`. ([docs.sqlalchemy.org][4])

---

# How to get all the blogs from the database?

```python
@app.get('/blog')
def all(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs
```

# How to get the blog with specific id?

```python
@app.get('/blog/{id}', status_code=status.HTTP_200_OK)
def show(id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    return blog
```

# Now talk about response codes and missing resources

* You can set a default response status code in the decorator. `from fastapi import status` gives helpful named constants like `status.HTTP_201_CREATED`. ([fastapi.tiangolo.com][6])

Return a **404** when the blog doesn’t exist:

```python
from fastapi import HTTPException, Response

@app.get('/blog/{id}', status_code=status.HTTP_200_OK)
def show(id: int, response: Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        # Option 1: set status code and return a detail
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'detail': f"Blog with the id {id} is not available"}
    return blog
```

Or better, raise an exception:

```python
@app.get('/blog/{id}', status_code=status.HTTP_200_OK)
def show(id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with id {id} not found"
        )
    return blog
```

*Use `raise HTTPException(...)` (don’t `return` it) to produce proper error responses.* ([fastapi.tiangolo.com][7])

---

# Now talk about delete operation

```python
@app.delete('/blog/{id}', status_code=status.HTTP_204_NO_CONTENT)
def destroy(id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with id {id} not found")
    db.delete(blog)
    db.commit()
```

*(Remember to `db.commit()` to persist deletes.)* ([docs.sqlalchemy.org][4])

---

# Now how to update?

```python
@app.put('/blog/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id: int, request: schemas.Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with id {id} not found")
    blog.title = request.title
    blog.body = request.body
    db.commit()
    db.refresh(blog)
    return blog
```

*(SQLAlchemy’s Session is the main interface for CRUD operations with ORM objects.)* ([docs.sqlalchemy.org][4])

---

## Built-in API Docs

* FastAPI provides **Swagger UI** at `/docs` and **ReDoc** at `/redoc`. ([fastapi.tiangolo.com][8])

---

## References

* FastAPI Tutorial – **SQL (Relational) Databases** (SQLite, `connect_args`, pattern): ([fastapi.tiangolo.com][1])
* FastAPI – **Dependencies with `yield`** (DB session per request): ([fastapi.tiangolo.com][5])
* FastAPI – **Handling Errors / HTTPException**: ([fastapi.tiangolo.com][7])
* FastAPI – **Response Status Code** (using `status` constants): ([fastapi.tiangolo.com][6])
* FastAPI – **Request Body** (Pydantic models): ([fastapi.tiangolo.com][2])
* SQLAlchemy – **ORM Quick Start** / **Using the Session**: ([docs.sqlalchemy.org][3])

*(I kept all correct points, fixed typos/bugs, and aligned code with current FastAPI/SQLAlchemy practices while preserving your original intent.)*

[1]: https://fastapi.tiangolo.com/tutorial/sql-databases/?utm_source=chatgpt.com "SQL (Relational) Databases"
[2]: https://fastapi.tiangolo.com/tutorial/body/?utm_source=chatgpt.com "Request Body - FastAPI"
[3]: https://docs.sqlalchemy.org/orm/quickstart.html?utm_source=chatgpt.com "ORM Quick Start — SQLAlchemy 2.0 Documentation"
[4]: https://docs.sqlalchemy.org/en/latest/orm/session.html?utm_source=chatgpt.com "Using the Session — SQLAlchemy 2.0 Documentation"
[5]: https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/?utm_source=chatgpt.com "Dependencies with yield"
[6]: https://fastapi.tiangolo.com/tutorial/path-operation-configuration/?utm_source=chatgpt.com "Path Operation Configuration"
[7]: https://fastapi.tiangolo.com/tutorial/handling-errors/?utm_source=chatgpt.com "Handling Errors"
[8]: https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/?utm_source=chatgpt.com "Path Operation Advanced Configuration"
