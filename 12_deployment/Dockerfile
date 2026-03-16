# Dockerfile — FastAPI Production Setup

# Base image
FROM python:3.11-slim

# Working directory
WORKDIR /app

# Dependencies pehle copy karo (caching ke liye)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code copy karo
COPY . .

# Port expose karo
EXPOSE 8000

# Production mein Gunicorn + Uvicorn workers use karo
CMD ["gunicorn", "main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "60", \
     "--access-logfile", "-"]
