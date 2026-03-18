# Docker Deployment Guide - Todo App Phase V

This guide covers deploying the Todo App using Docker with Neon Serverless PostgreSQL.

## Quick Reference

### Recommended Development Workflow (Backend Locally)

```powershell
# Windows - Start infrastructure + backend locally
.\start-dev.ps1

# Then in another terminal, start frontend
cd frontend && npm run dev
```

### Production Deployment

```bash
# Copy and configure environment
cp .env.example .env

# Build and run all services
docker-compose up -d --build
```

**Note:** The frontend container automatically connects to the backend container via Docker's internal network (`http://todo-backend:7860`).

---

## Prerequisites

- Docker Desktop installed
- Neon PostgreSQL database (get connection string from https://console.neon.tech/)
- OpenRouter API key (get from https://openrouter.ai/keys) - for AI chat feature

## Quick Start

### 1. Configure Environment Variables

Copy the `.env.example` file to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `DATABASE_URL` - Your Neon PostgreSQL connection string
- `JWT_SECRET` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `OPENROUTER_API_KEY` - Your OpenRouter API key

### 2. Production Deployment

Build and run all services (backend, frontend, Kafka, Redis):

```bash
docker-compose up -d --build
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:7860
- Kafka: localhost:9092
- Redis: localhost:6379

### 3. Development Mode (Recommended)

#### Option A: Backend Locally + Infrastructure in Docker

This is the recommended workflow for development. Backend runs locally with hot-reload, while Kafka and Redis run in Docker.

**Windows (PowerShell):**
```powershell
.\start-dev.ps1
```

**Linux/Mac:**
```bash
chmod +x start-dev.sh
./start-dev.sh
```

**Manual Setup:**
```bash
# Start infrastructure (Kafka, Redis) in Docker
docker-compose -f docker-compose.dev.yml up -d kafka zookeeper redis

# In another terminal, start backend locally
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 7860

# In a third terminal, start frontend
cd frontend
npm run dev
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:7860
- Kafka: localhost:9092
- Redis: localhost:6379

#### Option B: Full Docker Dev Environment

Run everything in Docker (frontend with hot-reload):

```bash
docker-compose -f docker-compose.dev.yml up -d --build
```

Note: You'll need to modify the backend service in `docker-compose.dev.yml` to uncomment the volume mounts for local code.

#### Option C: Frontend Only in Docker

Run backend and infrastructure locally, frontend in Docker:

```bash
# Start frontend in Docker (connects to host backend)
docker-compose -f docker-compose.dev-frontend.yml up -d --build
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| frontend | 3000 | Next.js web application |
| backend | 7860 | FastAPI backend API |
| kafka | 9092 | Event streaming (for async tasks) |
| zookeeper | 2181 | Kafka coordination |
| redis | 6379 | Celery broker/cache |

## Common Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuild Services

```bash
# Rebuild and restart
docker-compose up -d --build

# Force rebuild without cache
docker-compose build --no-cache
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (warning: deletes data)
docker-compose down -v
```

### Check Health

```bash
# Check service status
docker-compose ps

# Health check
curl http://localhost:7860/health
curl http://localhost:3000/health
```

## Environment Variables

### Required

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `JWT_SECRET` | Secret key for JWT tokens |
| `OPENROUTER_API_KEY` | API key for AI chat feature |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `API_PROVIDER` | openrouter | LLM provider (openrouter/gemini) |
| `CHAT_MODEL` | meta-llama/llama-3.2-3b-instruct:free | AI model to use |
| `SMTP_*` | - | Email configuration for reminders |
| `FRONTEND_URL` | http://localhost:3000 | Frontend base URL |

## Troubleshooting

### Backend won't start

1. Check DATABASE_URL is correct
2. Verify Neon database is accessible
3. Check logs: `docker-compose logs backend`

### Frontend shows connection error

1. Ensure backend is running and healthy
2. Check `NEXT_PUBLIC_API_BASE_URL` in Dockerfile
3. Verify network connectivity between containers

### Kafka connection issues

1. Wait for Kafka to fully start (can take 30-60 seconds)
2. Check logs: `docker-compose logs kafka`
3. Verify zookeeper is running first

## Architecture

### Production (docker-compose.yml)

```
┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│   Backend   │
│  (Next.js)  │     │  (FastAPI)  │
│  Port 3000  │     │  Port 7860  │
└─────────────┘     └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   Neon DB   │   │    Kafka    │   │    Redis    │
│ (Cloud)     │   │  Port 9092  │   │  Port 6379  │
└─────────────┘   └─────────────┘   └─────────────┘
```

### Development (Backend Locally + Docker Infrastructure)

```
┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│   Backend   │
│  (Next.js)  │     │  (FastAPI)  │
│  localhost  │     │  localhost  │
│  Port 3000  │     │  Port 7860  │
└─────────────┘     └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   Neon DB   │   │    Kafka    │   │    Redis    │
│ (Cloud)     │   │   Docker    │   │   Docker    │
│             │   │  Port 9092  │   │  Port 6379  │
└─────────────┘   └─────────────┘   └─────────────┘
```

## Security Notes

- Change `JWT_SECRET` in production
- Use environment variables for sensitive data
- Enable TLS/SSL for database connections
- Don't commit `.env` files to version control
