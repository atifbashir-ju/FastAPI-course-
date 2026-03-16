# main.py — Yeh woh app hai jisko hum test karenge

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="App to Test")

# In-memory DB
items_db: dict = {}
counter = {"id": 0}


class ItemCreate(BaseModel):
    name: str
    price: float
    in_stock: bool = True


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool


@app.get("/")
def home():
    return {"message": "App chal raha hai!"}


@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate):
    counter["id"] += 1
    new_item = {"id": counter["id"], **item.model_dump()}
    items_db[counter["id"]] = new_item
    return new_item


@app.get("/items", response_model=List[ItemResponse])
def get_items():
    return list(items_db.values())


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    item = items_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item nahi mila")
    return item


@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemCreate):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item nahi mila")
    updated = {"id": item_id, **item.model_dump()}
    items_db[item_id] = updated
    return updated


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item nahi mila")
    del items_db[item_id]
