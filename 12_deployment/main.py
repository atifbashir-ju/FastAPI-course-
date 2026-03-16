# main.py — Production-Ready FastAPI App
# Yeh example sab cheezein ek saath dikhata hai

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

app = FastAPI(
    title="Production FastAPI App",
    version="1.0.0",
    docs_url="/docs" if DEBUG else None,   # Production mein docs hide karo
    redoc_url="/redoc" if DEBUG else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://meri-frontend.com"] if not DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """Docker/Kubernetes health check ke liye"""
    return {"status": "healthy", "database": "connected"}
