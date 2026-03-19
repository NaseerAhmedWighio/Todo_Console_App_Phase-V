# Deployment Guide - Todo App Phase V

## Quick Fix for Current Issue

Your frontend is trying to connect to `localhost:7860` instead of your server's public IP.

### SSH into your server and run:

```bash
# Connect to server
ssh opc@80.225.210.147

# Navigate to app directory
cd /home/opc/hackathon

# Check if backend is running
docker ps -a | grep todo

# Check backend health
curl http://localhost:7860/health

# Check backend logs
docker logs todo-backend

# Stop old frontend
docker stop todo-frontend && docker rm todo-frontend

# Rebuild frontend with correct API URL
docker compose build frontend --build-arg NEXT_PUBLIC_API_BASE_URL=http://80.225.210.147:7860

# Start frontend
docker compose up -d frontend

# Check frontend logs
docker logs todo-frontend

# Verify both services are running
docker ps
```

## URLs

- **Frontend**: http://80.225.210.147:3000
- **Backend**: http://80.225.210.147:7860
- **Backend Health**: http://80.225.210.147:7860/health

## How to Check Backend Status

### Method 1: Docker Commands
```bash
# Check if container is running
docker ps | grep todo-backend

# Check container logs
docker logs todo-backend

# Check container health
docker inspect todo-backend --format='{{.State.Health.Status}}'
```

### Method 2: HTTP Health Check
```bash
# From server
curl http://localhost:7860/health

# From your local machine
curl http://80.225.210.147:7860/health
```

### Method 3: Docker Compose
```bash
cd /home/opc/hackathon
docker compose ps
docker compose logs backend
```

## Automated Deployment (CI/CD)

The workflow now automatically:
1. Builds frontend with correct API URL (`http://80.225.210.147:7860`)
2. Pushes images to DockerHub
3. Deploys to Oracle server
4. Rebuilds frontend on server with correct URL

### Trigger Deployment
1. Push to `master` branch → Auto-deploys
2. Manual trigger via GitHub Actions → Deploy Oracle workflow

## Architecture

```
┌─────────────────────┐
│   User Browser      │
│  http://80.225...147:3000 │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Frontend (Next.js)│
│   Port: 3000        │
│   API URL: Server IP│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Backend (FastAPI) │
│   Port: 7860        │
└──────────┬──────────┘
           │
           ├──► Kafka (9092)
           ├──► Redis (6379)
           └──► Neon DB (external)
```

## Environment Variables

Key variables in `.env`:
- `DATABASE_URL` - Neon PostgreSQL connection
- `JWT_SECRET` - JWT token signing
- `NEXT_PUBLIC_API_BASE_URL` - Frontend API URL (http://SERVER_IP:7860)
- `OPENROUTER_API_KEY` - AI provider key
- `SMTP_*` - Email configuration

## Troubleshooting

### Frontend can't connect to backend
1. Check backend is running: `docker ps | grep todo-backend`
2. Check backend logs: `docker logs todo-backend`
3. Test backend directly: `curl http://localhost:7860/health`
4. Rebuild frontend with correct URL

### Backend not starting
1. Check logs: `docker logs todo-backend`
2. Verify .env file exists with all required variables
3. Check database connection: `docker exec todo-backend ping -c 3 your-db-host`

### CORS errors
- Ensure `NEXT_PUBLIC_API_BASE_URL` matches your server IP
- Rebuild frontend after changing the URL
- Clear browser cache

## Commands Reference

```bash
# View all containers
docker ps -a

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Restart services
docker compose restart

# Full rebuild
docker compose down
docker compose build --no-cache
docker compose up -d

# Check resource usage
docker stats
```
