# Docker Container Networking Configuration

## Overview

This document explains how the frontend and backend containers communicate in different deployment scenarios.

## Production Deployment (docker-compose.yml)

### Container Communication

In production, all services run in Docker containers on a shared network called `todo-network`.

```
┌─────────────────────────────────────────────────────────┐
│                   todo-network (bridge)                  │
│                                                          │
│  ┌──────────────┐      ┌──────────────┐                 │
│  │   Frontend   │─────▶│    Backend   │                 │
│  │  Container   │      │   Container  │                 │
│  │ todo-frontend│      │  todo-backend│                 │
│  │  Port 3000   │      │   Port 7860  │                 │
│  └──────────────┘      └──────┬───────┘                 │
│                               │                          │
│         ┌─────────────────────┼──────────────┐           │
│         │                     │              │           │
│         ▼                     ▼              ▼           │
│  ┌────────────┐       ┌────────────┐ ┌────────────┐     │
│  │   Kafka    │       │   Redis    │ │  Neon DB   │     │
│  │ Container  │       │ Container  │ │  (Cloud)   │     │
│  │ Port 9092  │       │ Port 6379  │ │            │     │
│  └────────────┘       └────────────┘ └────────────┘     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Key Configuration

**Frontend connects to Backend:**
- URL: `http://todo-backend:7860`
- Uses Docker service name for internal communication
- Configured via build argument in docker-compose.yml

**Backend connects to:**
- Kafka: `kafka:29092` (service name)
- Redis: `redis:6379` (service name)
- Neon DB: Cloud URL (from environment variable)

### docker-compose.yml Configuration

```yaml
frontend:
  build:
    args:
      - NEXT_PUBLIC_API_BASE_URL=http://todo-backend:7860
  networks:
    - todo-network

backend:
  container_name: todo-backend
  networks:
    - todo-network
```

## Development Deployment (docker-compose.dev.yml)

### Container Communication

In development, the backend runs locally on your host machine, while frontend, Kafka, and Redis run in Docker.

```
┌─────────────────────────────────────────────────────────┐
│              Host Machine (localhost)                    │
│  ┌──────────────┐                                       │
│  │    Backend   │  Port 7860                            │
│  │  (uvicorn)   │                                       │
│  └──────┬───────┘                                       │
│         │                                               │
└─────────│───────────────────────────────────────────────┘
          │
          │ host.docker.internal:7860
          │
┌─────────│───────────────────────────────────────────────┐
│         │              Docker Containers                 │
│         ▼                                               │
│  ┌──────────────┐      ┌──────────────┐                 │
│  │   Frontend   │      │    Kafka     │                 │
│  │   Container  │      │   Container  │                 │
│  │ todo-frontend│      │  kafka-dev   │                 │
│  │  Port 3000   │      │   Port 9092  │                 │
│  └──────────────┘      └──────────────┘                 │
│                               │                          │
│                               ▼                          │
│                        ┌────────────┐                    │
│                        │   Redis    │                    │
│                        │ Container  │                    │
│                        │ Port 6379  │                    │
│                        └────────────┘                    │
│                                                          │
│              todo-network-dev (bridge)                   │
└─────────────────────────────────────────────────────────┘
```

### Key Configuration

**Frontend connects to Backend:**
- URL: `http://host.docker.internal:7860`
- Uses special Docker DNS to reach host machine
- Configured via environment variable

**Frontend connects to Kafka/Redis:**
- Uses Docker service names within the same network
- Kafka: `kafka:29092`
- Redis: `redis:6379`

### docker-compose.dev.yml Configuration

```yaml
frontend:
  environment:
    - NEXT_PUBLIC_API_BASE_URL=http://host.docker.internal:7860
  extra_hosts:
    - "host.docker.internal:host-gateway"
  networks:
    - todo-network-dev
```

## Frontend Only Deployment (docker-compose.dev-frontend.yml)

Use this when both backend and infrastructure run locally.

```yaml
frontend:
  environment:
    - NEXT_PUBLIC_API_BASE_URL=http://host.docker.internal:7860
  extra_hosts:
    - "host.docker.internal:host-gateway"
```

## How It Works

### Production Flow

1. User accesses `http://localhost:3000` → Frontend container
2. Frontend makes API calls to `http://todo-backend:7860`
3. Docker DNS resolves `todo-backend` to backend container IP
4. Backend processes request and responds
5. Frontend receives response and updates UI

### Development Flow

1. User accesses `http://localhost:3000` → Frontend container
2. Frontend makes API calls to `http://host.docker.internal:7860`
3. Docker routes to host machine's localhost:7860
4. Local backend (uvicorn) processes request
5. Response returns through the same path

## Network Configuration

### Production Network

```yaml
networks:
  todo-network:
    driver: bridge
```

All services are attached to this network, enabling container-to-container communication.

### Development Network

```yaml
networks:
  todo-network-dev:
    driver: bridge
```

Frontend, Kafka, and Redis are on this network. Backend is on host machine.

## Environment Variables

### Production (.env)

```bash
# Frontend build argument (set in docker-compose.yml)
NEXT_PUBLIC_API_BASE_URL=http://todo-backend:7860

# Backend environment
FRONTEND_URL=http://todo-frontend:3000
```

### Development (backend/.env)

```bash
# Frontend .env.local (optional, defaults to localhost)
NEXT_PUBLIC_API_BASE_URL=http://localhost:7860

# Backend .env
FRONTEND_URL=http://localhost:3000
```

## Troubleshooting

### Frontend can't connect to Backend

**Check container names:**
```bash
docker-compose ps
```

**Test backend from frontend container:**
```bash
docker exec todo-frontend wget -qO- http://todo-backend:7860/health
```

**Check network:**
```bash
docker network inspect todo-network
```

### Development: "Cannot connect to host.docker.internal"

**On Windows/Mac:** This should work automatically with Docker Desktop.

**On Linux:** Add to `/etc/hosts`:
```
172.17.0.1 host.docker.internal
```

### Build fails with API URL error

**Clear build cache:**
```bash
docker-compose build --no-cache frontend
```

**Verify build argument:**
```bash
docker-compose config
```

## Quick Commands

```bash
# View container logs
docker-compose logs -f frontend
docker-compose logs -f backend

# Inspect network
docker network inspect todo-network

# Test connectivity
docker exec todo-frontend ping todo-backend
docker exec todo-frontend curl http://todo-backend:7860/health

# Restart specific service
docker-compose restart frontend
docker-compose restart backend
```

## Security Notes

- Production uses internal Docker network (not exposed to public)
- Only frontend ports (3000) are exposed to host
- Backend API (7860) is only accessible via frontend container
- Kafka/Redis are only accessible within Docker network
- Neon DB connection uses SSL/TLS (sslmode=require)
