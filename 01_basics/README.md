# 01 - FastAPI Basics

## Kya seekhoge
- FastAPI app kaise banate hain
- GET, POST, PUT, DELETE routes
- Path parameters (`/users/{id}`)
- Query parameters (`/items?search=phone`)
- Request body (POST/PUT ke liye)

## Run karo
```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

## Test karo
Swagger UI: http://127.0.0.1:8000/docs

| Route | Method | Kya karta hai |
|-------|--------|--------------|
| `/` | GET | Home page |
| `/users/{id}` | GET | User by ID |
| `/items` | GET | Items list (with search & pagination) |
| `/items` | POST | Naya item banao |
| `/items/{id}` | PUT | Item update karo |
| `/items/{id}` | DELETE | Item delete karo |
