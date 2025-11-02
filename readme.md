- fastapi provides auto docs with swagger ui and redocs ui(/docs and /redocs)
- python3.6 with type hints using Pydantic 
- based on an open standard:
  - Json schema: By refaults supporst return json
  - open standards: Define how you build api
- Code editore auto complete features
- Security and authentication:
   - Http base
   - OAuth2(also with just token)
   - API key in headers, query parameter, cookies
- Testing using pytest
- Suppors web socket, GraphQl, in proess background task, start up and shutdown events
- SQL, NOSQL, GraphQL



** Seturp **
```
mkdir project_name
cd project_name
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi
pip install uvicorn
```

** create main.py **
```python
from fastapi import FastAPI

//creating instance
app = FastAPI()

def index():
    return "hey"
```

** Run **
```
uvicorn main:app --reload
```
- in `127.0.0.1:80000` will show `{"detail" : "Not Found"}`
- So, we need to define path function

** Add decorator for defining path function **
```python
from fastapi import FastAPI

//creating instance
app = FastAPI()

@app.get('/)
def index():
    return "hey"
```

- So, yes, we have built the most straightforward fastApi api. That's all.

**4 Steps**
- Import
- Instnace
- Function
- Decoreate


