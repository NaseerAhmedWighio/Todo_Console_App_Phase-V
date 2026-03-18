# 🐳 Docker Image Build Guide

## Overview
This guide explains how to build Docker images for the Todo App Phase-V frontend and backend.

---

## 📋 Prerequisites

1. **Docker Desktop** installed and running
2. **Stable internet connection** (for pulling base images)
3. **Sufficient disk space** (~2-3 GB for both images)

---

## 🚀 Quick Start

### Build Both Images (PowerShell)

```powershell
# Navigate to project root
cd D:\Hackathon\todo-app-phase-V

# Build backend image
docker build -t todo-backend:latest ./backend

# Build frontend image
docker build -t todo-frontend:latest ./frontend

# Verify images
docker images | Select-String "todo-"
```

### Build Both Images (Bash/Linux)

```bash
cd /path/to/todo-app-phase-V

# Build backend
docker build -t todo-backend:latest ./backend

# Build frontend
docker build -t todo-frontend:latest ./frontend

# List images
docker images | grep todo
```

---

## 📦 Image Details

### Backend Image (`todo-backend:latest`)

| Property | Value |
|----------|-------|
| **Base Image** | python:3.11-slim |
| **Port** | 7860 |
| **Size** | ~500MB - 800MB |
| **Health Check** | GET /health |
| **User** | root (simplified) |

**Technologies:**
- FastAPI
- SQLModel
- Uvicorn
- PostgreSQL client (libpq5)

### Frontend Image (`todo-frontend:latest`)

| Property | Value |
|----------|-------|
| **Base Image** | node:18-alpine |
| **Port** | 3000 |
| **Size** | ~150MB - 200MB |
| **Health Check** | GET /health |
| **User** | nextjs (non-root) |

**Technologies:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS

---

## 🔧 Build Commands Reference

### 1. Build Backend Image

```powershell
cd D:\Hackathon\todo-app-phase-V\backend
docker build -t todo-backend:latest .
```

**What it does:**
- Uses `python:3.11-slim` base image
- Installs system dependencies (gcc, g++, libpq5, curl)
- Installs Python packages from `requirements.txt`
- Copies application code
- Exposes port 7860
- Configures health check on `/health`

### 2. Build Frontend Image

```powershell
cd D:\Hackathon\todo-app-phase-V\frontend
docker build -t todo-frontend:latest .
```

**What it does:**
- Multi-stage build with 3 stages (deps, builder, runner)
- Installs Node.js dependencies
- Builds Next.js application with `npm run build`
- Creates minimal production image with standalone output
- Exposes port 3000
- Configures health check on `/health`

### 3. Verify Images

```powershell
# List all todo images
docker images | Select-String "todo-"

# Detailed image info
docker inspect todo-backend:latest
docker inspect todo-frontend:latest

# Check image size
docker images todo-backend:latest --format "{{.Size}}"
docker images todo-frontend:latest --format "{{.Size}}"
```

### 4. Test Images Locally

```powershell
# Run backend container
docker run -d --name todo-backend-test -p 7860:7860 todo-backend:latest

# Run frontend container
docker run -d --name todo-frontend-test -p 3000:3000 todo-frontend:latest

# Check logs
docker logs todo-backend-test
docker logs todo-frontend-test

# Test health endpoints
curl http://localhost:7860/health
curl http://localhost:3000/health

# Stop containers
docker stop todo-backend-test todo-frontend-test
docker rm todo-backend-test todo-frontend-test
```

---

## 🏗️ Kubernetes Deployment

### Load Images into Minikube

```powershell
# Start Minikube
minikube start --cpus=4 --memory=4096

# Load images
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# Verify
minikube image ls | Select-String "todo-"
```

### Deploy to Kubernetes

```powershell
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy Dapr components
kubectl apply -f dapr/components/kubernetes-components.yaml -n todo-app

# Deploy secrets (update with your DB credentials first)
kubectl apply -f k8s/secrets.yaml -n todo-app

# Deploy backend
kubectl apply -f k8s/backend-deployment.yaml -n todo-app

# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml -n todo-app

# Check status
kubectl get pods -n todo-app
kubectl get deployments -n todo-app
```

### Access Application

```powershell
# Port forward backend
kubectl port-forward svc/todo-backend 7860:7860 -n todo-app

# Port forward frontend
kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app

# Or use Minikube service
minikube service todo-frontend -n todo-app
```

---

## ☁️ Push to Registry (For Cloud Deployment)

### Docker Hub

```powershell
# Login to Docker Hub
docker login

# Tag images
docker tag todo-backend:latest yourusername/todo-backend:latest
docker tag todo-frontend:latest yourusername/todo-frontend:latest

# Push images
docker push yourusername/todo-backend:latest
docker push yourusername/todo-frontend:latest
```

### GitHub Container Registry

```powershell
# Login to GHCR
echo $GHCR_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Tag images
docker tag todo-backend:latest ghcr.io/YOUR_USERNAME/todo-backend:latest
docker tag todo-frontend:latest ghcr.io/YOUR_USERNAME/todo-frontend:latest

# Push images
docker push ghcr.io/YOUR_USERNAME/todo-backend:latest
docker push ghcr.io/YOUR_USERNAME/todo-frontend:latest
```

### Oracle Container Registry

```powershell
# Login to Oracle Registry
docker login registry.oraclecloud.io

# Tag images
docker tag todo-backend:latest registry.oraclecloud.io/YOUR_NAMESPACE/todo-backend:latest
docker tag todo-frontend:latest registry.oraclecloud.io/YOUR_NAMESPACE/todo-frontend:latest

# Push images
docker push registry.oraclecloud.io/YOUR_NAMESPACE/todo-backend:latest
docker push registry.oraclecloud.io/YOUR_NAMESPACE/todo-frontend:latest
```

---

## 🔍 Troubleshooting

### Issue: "dial tcp: lookup registry-1.docker.io: no such host"

**Solution:** Check your internet connection and DNS settings.

```powershell
# Test DNS resolution
nslookup registry-1.docker.io

# Try restarting Docker Desktop
# Docker Desktop → Troubleshoot → Restart
```

### Issue: "Cannot connect to the Docker daemon"

**Solution:** Ensure Docker Desktop is running.

```powershell
# Check Docker status
docker info

# Restart Docker Desktop if needed
```

### Issue: Build fails with "No such file or directory"

**Solution:** Check that you're in the correct directory and Dockerfile exists.

```powershell
# Verify Dockerfile exists
ls ./backend/Dockerfile
ls ./frontend/Dockerfile
```

### Issue: "Cannot start service: Bind for 0.0.0.0:3000 failed: address already in use"

**Solution:** Stop any process using the port or use a different port.

```powershell
# Find process using port 3000
netstat -ano | findstr :3000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or use different port
docker run -d -p 3001:3000 todo-frontend:latest
```

### Issue: Image build is slow

**Solution:** Use build cache and optimize Dockerfile.

```powershell
# Build with cache
docker build --cache-from todo-backend:latest -t todo-backend:latest ./backend

# Or build without cache (if cache is corrupted)
docker build --no-cache -t todo-backend:latest ./backend
```

---

## 📊 Image Optimization Tips

### Current Optimizations

✅ Multi-stage builds (frontend)
✅ Minimal base images (slim, alpine)
✅ Layer caching (copy requirements first)
✅ No cache installation (`--no-cache-dir`)
✅ Non-root users (security)
✅ Health checks configured

### Further Optimization (Optional)

```dockerfile
# Add to .dockerignore to reduce context size
.git
*.md
tests/
.env
logs/
```

---

## 🎯 Next Steps

After building images:

1. **Test locally** with `docker run`
2. **Test with docker-compose**: `docker-compose up -d`
3. **Deploy to Minikube** for Kubernetes testing
4. **Push to registry** for cloud deployment
5. **Deploy to Oracle OKE** (or other cloud provider)

---

## 📝 Image Tags Convention

| Tag | Description |
|-----|-------------|
| `latest` | Most recent build (default) |
| `v1.0.0` | Specific version |
| `dev` | Development build |
| `staging` | Pre-production build |
| `prod` | Production build |

**Example:**
```powershell
docker build -t todo-backend:v1.0.0 -t todo-backend:latest ./backend
```

---

## 🔗 Related Documentation

- [PHASE_V_DEPLOYMENT.md](PHASE_V_DEPLOYMENT.md) - Complete deployment guide
- [README.md](README.md) - Project overview
- [k8s/](k8s/) - Kubernetes manifests
- [dapr/components/](dapr/components/) - Dapr configurations

---

**Build successful? You're ready to deploy!** 🚀
