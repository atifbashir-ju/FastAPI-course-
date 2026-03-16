# 03 - Response Models & Error Handling
# Topics: response_model, status codes, HTTPException, custom exception handlers

from typing import Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Response & Error Handling")

# Fake database
fake_users_db = {
    1: {"id": 1, "name": "Ali Hassan", "email": "ali@gmail.com", "is_active": True},
    2: {"id": 2, "name": "Sara Khan", "email": "sara@gmail.com", "is_active": False},
}


# ─── Models ──────────────────────────────────────────────────────────────────
class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class UserCreate(BaseModel):
    name: str
    email: str


# ─── 1. Response Model ───────────────────────────────────────────────────────
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    user = fake_users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} nahi mila",
        )
    return user


# ─── 2. Custom Status Codes ──────────────────────────────────────────────────
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    new_id = max(fake_users_db.keys()) + 1
    new_user = {"id": new_id, **user.model_dump()}
    fake_users_db[new_id] = new_user
    return new_user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="User nahi mila")
    del fake_users_db[user_id]
    # 204 = No Content, kuch return nahi karte


# ─── 3. Different error scenarios ────────────────────────────────────────────
@app.get("/users/{user_id}/activate")
def activate_user(user_id: int):
    user = fake_users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User nahi mila")
    if user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User pehle se active hai",
        )
    user["is_active"] = True
    return {"message": "User activate ho gaya", "user": user}


# ─── 4. Custom Exception Class ───────────────────────────────────────────────
class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id


@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Item Not Found",
            "message": f"Item ID {exc.item_id} database mein nahi hai",
            "hint": "Sahi ID check karo",
        },
    )


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id > 100:
        raise ItemNotFoundError(item_id=item_id)
    return {"item_id": item_id, "name": f"Item {item_id}"}


# ─── 5. Global Exception Handler ─────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Server Error", "message": "Kuch gadbad ho gayi, baad mein try karo"},
    )


# ─── 6. Optional Response ────────────────────────────────────────────────────
@app.get("/users/{user_id}/profile", response_model=Optional[UserResponse])
def get_user_profile(user_id: int):
    user = fake_users_db.get(user_id)
    return user  # None return karna bhi valid hai
