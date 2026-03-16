# main.py — FastAPI + SQLAlchemy CRUD

from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

import models, schemas
from database import engine, get_db

# Tables create karo (agar exist nahi karti)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI + SQLAlchemy")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── Users CRUD ───────────────────────────────────────────────────────────────
@app.post("/users", response_model=schemas.UserResponse, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Email already exists?
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email pehle se registered hai")

    hashed_pw = pwd_context.hash(user.password)
    db_user = models.User(name=user.name, email=user.email, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users", response_model=List[schemas.UserResponse])
def get_all_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.User).offset(skip).limit(limit).all()


@app.get("/users/{user_id}", response_model=schemas.UserWithPosts)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User nahi mila")
    return user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User nahi mila")
    db.delete(user)
    db.commit()


# ─── Posts CRUD ───────────────────────────────────────────────────────────────
@app.post("/users/{user_id}/posts", response_model=schemas.PostResponse, status_code=201)
def create_post(user_id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User nahi mila")

    db_post = models.Post(**post.model_dump(), author_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.get("/posts", response_model=List[schemas.PostResponse])
def get_all_posts(published: bool = None, db: Session = Depends(get_db)):
    query = db.query(models.Post)
    if published is not None:
        query = query.filter(models.Post.published == published)
    return query.all()


@app.get("/posts/{post_id}", response_model=schemas.PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post nahi mila")
    return post


@app.patch("/posts/{post_id}", response_model=schemas.PostResponse)
def update_post(post_id: int, post_data: schemas.PostUpdate, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post nahi mila")

    update_data = post_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(post, key, value)

    db.commit()
    db.refresh(post)
    return post


@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post nahi mila")
    db.delete(post)
    db.commit()
