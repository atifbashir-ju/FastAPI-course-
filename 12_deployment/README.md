# 12 - Deployment

## Docker ke saath run karo

```bash
# Build aur start karo (sab services — app + db + redis)
docker-compose up --build

# Background mein chalaao
docker-compose up -d

# Logs dekho
docker-compose logs -f api

# Band karo
docker-compose down
```

## Sirf app test karo (bina docker-compose)

```bash
docker build -t fastapi-app .
docker run -p 8000:8000 fastapi-app
```

## .env setup

```bash
cp .env.example .env
# .env file mein apni values daalo
```

## Production checklist

- [ ] `.env` file mein real SECRET_KEY daalo
- [ ] `DEBUG=false` karo
- [ ] `.env` ko `.gitignore` mein daalo
- [ ] HTTPS enable karo (Nginx ya Traefik)
- [ ] Database backups setup karo
