# 🚀 FastAPI Complete Course

Yeh repository ek complete FastAPI course hai — beginner se production-ready tak.
Har folder ek topic cover karta hai with working code examples.

## 📁 Folder Structure

```
fastapi-course/
├── 01_basics/              → Routing, Path/Query Params, Request Body
├── 02_pydantic_models/     → Validation, Schema, Custom Validators
├── 03_response_and_errors/ → Response Models, Status Codes, Exceptions
├── 04_database_sqlalchemy/ → SQLAlchemy ORM, CRUD, Migrations
├── 05_authentication_jwt/  → JWT Auth, OAuth2, Login/Register
├── 06_dependencies/        → Depends(), Reusable logic, Auth Guard
├── 07_middleware_cors/     → CORS, Custom Middleware, Logging
├── 08_file_upload/         → File Upload/Download, Form Data
├── 09_background_tasks/    → BackgroundTasks, Celery + Redis
├── 10_websockets/          → WebSocket, Real-time Chat
├── 11_testing/             → pytest, TestClient, Fixtures
└── 12_deployment/          → Docker, docker-compose, Gunicorn
```

## ⚙️ Setup

```bash
pip install fastapi uvicorn sqlalchemy pydantic[email] python-jose passlib bcrypt python-multipart
```

## ▶️ Run any example

```bash
cd 01_basics
uvicorn main:app --reload
```

Phir browser mein jaao: `http://127.0.0.1:8000/docs`

---
Made for learning FastAPI from scratch to production 💪
