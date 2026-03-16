# schemas.py — Pydantic Schemas (Request/Response shapes)

from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


# ─── User Schemas ─────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # ORM objects ko dict mein convert karta hai


class UserWithPosts(UserResponse):
    posts: List["PostResponse"] = []


# ─── Post Schemas ─────────────────────────────────────────────────────────────
class PostCreate(BaseModel):
    title: str
    content: str
    published: bool = False


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    author_id: int

    class Config:
        from_attributes = True


# Forward reference fix
UserWithPosts.model_rebuild()
