# main.py — JWT Auth with FastAPI
# Topics: Register, Login, Protected routes, Current user

from datetime import timedelta
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

app = FastAPI(title="JWT Authentication")

# OAuth2 scheme — /token route se token lega
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Fake database (04 mein real DB dekha tha)
fake_users_db = {}


# ─── Schemas ─────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str


# ─── Dependency: Current logged-in user ──────────────────────────────────────
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalid ya expire ho gaya",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token)
    if not token_data:
        raise credentials_exception

    user = fake_users_db.get(token_data.email)
    if not user:
        raise credentials_exception
    return user


# ─── Routes ──────────────────────────────────────────────────────────────────
@app.post("/register", response_model=UserResponse, status_code=201)
def register(user: UserCreate):
    if user.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Email pehle se registered hai")

    user_id = len(fake_users_db) + 1
    fake_users_db[user.email] = {
        "id": user_id,
        "name": user.name,
        "email": user.email,
        "hashed_password": hash_password(user.password),
    }
    return fake_users_db[user.email]


@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2PasswordRequestForm mein username aur password hote hain
    user = fake_users_db.get(form_data.username)  # username = email
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ya password galat hai",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ─── Protected Routes (Login required) ───────────────────────────────────────
@app.get("/me", response_model=UserResponse)
def get_my_profile(current_user: dict = Depends(get_current_user)):
    return current_user


@app.get("/dashboard")
def dashboard(current_user: dict = Depends(get_current_user)):
    return {
        "message": f"Welcome {current_user['name']}!",
        "your_email": current_user["email"],
    }


@app.get("/users", response_model=List[UserResponse])
def get_all_users(current_user: dict = Depends(get_current_user)):
    # Sirf logged-in user dekh sakta hai
    return list(fake_users_db.values())
