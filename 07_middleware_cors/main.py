# 07 - Middleware & CORS
# Topics: CORS setup, custom middleware, logging, request timing

import time
import uuid
import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Middleware & CORS")


# ─── 1. CORS Middleware ───────────────────────────────────────────────────────
# Frontend (React/Vue) alag port pe hoti hai, isliye CORS zaroori hai
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React dev server
        "http://localhost:5173",   # Vite dev server
        "https://meri-site.com",   # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],           # GET, POST, PUT, DELETE sab allow
    allow_headers=["*"],
)


# ─── 2. Custom Middleware — Request Timing ────────────────────────────────────
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # milliseconds
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response


# ─── 3. Custom Middleware — Request ID (tracing ke liye) ─────────────────────
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ─── 4. Custom Middleware — Logging ──────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"→ {request.method} {request.url.path}")
    response: Response = await call_next(request)
    logger.info(f"← {response.status_code} {request.url.path}")
    return response


# ─── 5. Trusted Host Middleware ───────────────────────────────────────────────
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["myapp.com", "*.myapp.com", "localhost"]
# )
# (commented — dev mein disable rakho)


# ─── Routes ──────────────────────────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "Middleware test karo — response headers dekho!"}


@app.get("/slow")
async def slow_route():
    time.sleep(0.5)  # Simulate slow operation
    return {"message": "Yeh thoda slow tha"}


@app.get("/headers")
async def show_request_headers(request: Request):
    return {"headers": dict(request.headers)}
