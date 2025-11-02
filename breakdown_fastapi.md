# Fist we need to understand `app = FastAPI()` in `main.py`

- `uvicorn main: app --reload` here main = file name and app = fastAPI instacne
- if the instache name = myapp the command will be `uvicorn main: myapp --reload`
- if the file name = mehedi the command will be `uvicorn mehed: app --reload`


# Second is that the function name under decorator does not matter. we can use the same function name for differenct decorators.

```python
app.get('/')

def abc():
    return {'data': 'this is from / path'}

add.get('/about'):
    return {'data': 'this is from /about path'}

```

- so matter only decorator

# Third, `@app.get('/about')`  here,
- @app = @instache
- get() = operation on path
- '/about' called path on fastApi (router on other frameworks)

# Fourth, `def abc():` is called a path operation function in which above we are defining the operation on the path.
- this is the operation/opetations we are going to perform on the route.

# Fourth, Dynamic route
- for dynami routing use `/{}` and `need to accept this variable` in `the path operation function`.
```python
@app.get('/blog/{id}')

def show(id):
    return {'data': id}
```
- If we hit `http://127.0.0.1:8000/blog/unpublished`, the output will look like `{'data': "3"}`. But, we need id as `integer`
- Here comes type hints. this will `convert compatible type into the target type`. in this case, `a string of number in string`.
```python
@app.get('/blog/{id}')

def show(id:int):
    return {'data': id}
```

- But, if they are not compatible. it will show
```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": [
        "path",
        "id"
      ],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "unpublished"
    }
  ]
}
```

# Fifth, fast api reads code line by line
```python
@app.get('/blog/{id}')
def show(id:int):
    return {'data': id}

@app.get('/blog/unpublished')
def unpublished():
    return {'data': 'all unpublished blogs'}
```

- if we hit `http://127.0.0.1:8000/blog/unpublished` this will show. because fast api reads file line by line and go to show() method.
```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": [
        "path",
        "id"
      ],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "unpublished"
    }
  ]
}
```

- solution = whever you crate dynamic route you have to take care of routers which matches with the route and move them before the dynamic route 

```python
@app.get('/blog/unpublished')
def unpublished():
    return {'data': 'all unpublished blogs'}

@app.get('/blog/{id}')
def show(id:int):
    return {'data': id}
```

N.B : Al lthe data validation is performed under the hood by Pydantic, so you will get all the bebefits form it. 
