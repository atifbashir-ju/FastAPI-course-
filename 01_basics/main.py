# 01 - FastAPI Basics
# Topics: App setup, routing, path params, query params, request body

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="FastAPI Basics", version="1.0")


# ─── 1. Simple GET route ────────────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "FastAPI mein Welcome!"}


# ─── 2. Path Parameters ─────────────────────────────────────────────────────
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "name": f"User {user_id}"}


# ─── 3. Query Parameters ────────────────────────────────────────────────────
# URL: /items?skip=0&limit=10&search=phone
@app.get("/items")
def get_items(skip: int = 0, limit: int = 10, search: str = None):
    items = ["phone", "laptop", "tablet", "headphones", "charger"]
    if search:
        items = [i for i in items if search.lower() in i]
    return {"items": items[skip : skip + limit], "total": len(items)}


# ─── 4. Request Body (POST) ──────────────────────────────────────────────────
class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True


@app.post("/items")
def create_item(item: Item):
    return {"message": "Item create ho gaya!", "item": item}


# ─── 5. PUT - Update ─────────────────────────────────────────────────────────
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_id": item_id, "updated_item": item}


# ─── 6. DELETE ───────────────────────────────────────────────────────────────
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"message": f"Item {item_id} delete ho gaya"}


# ─── 7. Path + Query + Body (combined) ───────────────────────────────────────
@app.put("/users/{user_id}/items/{item_id}")
def update_user_item(
    user_id: int,
    item_id: int,
    item: Item,
    verified: bool = False,
):
    return {
        "user_id": user_id,
        "item_id": item_id,
        "item": item,
        "verified": verified,
    }
