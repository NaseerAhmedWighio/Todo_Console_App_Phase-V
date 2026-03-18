# 🐳 Docker & Kubernetes Deployment - Complete Guide

## 📋 What Was Created

Your Todo App Phase-V now has **complete Docker and Kubernetes deployment support** with the following files:

### ✅ Docker Configuration
```
backend/
  ├── Dockerfile              # ✅ Created - FastAPI container (port 7860)
  └── .dockerignore           # ✅ Created - Build exclusions

frontend/
  ├── Dockerfile              # ✅ Created - Next.js container (port 3000)
  └── .dockerignore           # ✅ Created - Build exclusions
```

### ✅ Build Scripts
```
build-docker-images.ps1       # ✅ Created - PowerShell build script
build-docker-images.sh        # ✅ Created - Bash build script
```

### ✅ Documentation
```
QUICK_DEPLOY.md               # ✅ START HERE - Quick start guide
DEPLOYMENT_SUMMARY.md         # ✅ Complete deployment overview
DOCKER_BUILD_GUIDE.md         # ✅ Detailed Docker instructions
KUBERNETES_DEPLOYMENT_GUIDE.md # ✅ K8s + Oracle OKE deployment
```

### ✅ Kubernetes Configuration
```
k8s/
  ├── namespace.yaml                    # ✅ Namespace definition
  ├── backend-deployment.yaml           # ✅ Updated to port 7860
  ├── frontend-deployment.yaml          # ✅ Frontend deployment
  ├── kafka-cluster.yaml                # ✅ Kafka (Strimzi)
  └── secrets.yaml                      # ✅ DB secrets

dapr/components/
  └── kubernetes-components.yaml        # ✅ Dapr pubsub, state, secrets
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Build Docker Images

```powershell
cd D:\Hackathon\todo-app-phase-V

# Run build script
.\build-docker-images.ps1

# Or build manually:
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend
```

**Expected Output:**
```
>>> Backend image built successfully!
>>> Frontend image built successfully!

Backend Image:
REPOSITORY     TAG      IMAGE ID       SIZE
todo-backend   latest   abc123456      650MB

Frontend Image:
REPOSITORY       TAG      IMAGE ID       SIZE
todo-frontend    latest   def789012      180MB
```

### Step 2: Test Locally

```powershell
# Start with Docker Compose
docker-compose up -d

# Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8001
# Health: http://localhost:8001/health
```

### Step 3: Deploy to Kubernetes

#### Option A: Minikube (Local)
```powershell
minikube start --cpus=4 --memory=4096
dapr init -k
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

kubectl apply -f k8s/namespace.yaml
kubectl apply -f dapr/components/kubernetes-components.yaml -n todo-app
kubectl apply -f k8s/secrets.yaml -n todo-app
kubectl apply -f k8s/backend-deployment.yaml -n todo-app
kubectl apply -f k8s/frontend-deployment.yaml -n todo-app

minikube service todo-frontend -n todo-app
```

#### Option B: Oracle OKE (Cloud - Always Free)
```powershell
# 1. Create OKE Cluster in Oracle Cloud Console
# 2. Download kubeconfig
oci ce cluster create-kubeconfig --cluster-id <OCID> --file $HOME\.kube\config

# 3. Push images to Oracle Registry
docker login registry.oraclecloud.io
docker tag todo-backend:latest registry.oraclecloud.io/YOUR_NAMESPACE/todo-backend:latest
docker push registry.oraclecloud.io/YOUR_NAMESPACE/todo-backend:latest

# 4. Deploy
kubectl apply -f k8s/
dapr init -k

# 5. Expose
kubectl expose deployment todo-frontend --type=LoadBalancer --port=80 -n todo-app
kubectl get svc -n todo-app
```

---

## 🏗️ Architecture Overview

### Deployment Flow

```
┌─────────────────────────────────────────────────────────────┐
│  BUILD                                                        │
│  ┌─────────────┐  ┌─────────────┐                           │
│  │   Backend   │  │  Frontend   │                           │
│  │  Dockerfile │  │  Dockerfile │                           │
│  └──────┬──────┘  └──────┬──────┘                           │
│         │                │                                   │
│         ▼                ▼                                   │
│  ┌─────────────┐  ┌─────────────┐                           │
│  │ todo-backend│  │todo-frontend│                           │
│  │   :latest   │  │   :latest   │                           │
│  └──────┬──────┘  └──────┬──────┘                           │
└─────────┼────────────────┼───────────────────────────────────┘
          │                │
          ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│  DEPLOY                                                     │
│  ┌─────────────┐  ┌─────────────┐                           │
│  │   Docker    │  │ Kubernetes  │                           │
│  │   Compose   │  │  (Minikube/ │                           │
│  │  (Local)    │  │   OKE)      │                           │
│  └─────────────┘  └─────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

### Runtime Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER                         │
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │   Frontend   │         │   Backend    │                  │
│  │  Pod + Dapr  │────────▶│  Pod + Dapr  │                  │
│  │  (Next.js)   │         │  (FastAPI)   │                  │
│  │  Port 3000   │         │  Port 7860   │                  │
│  └──────────────┘         └──────┬───────┘                  │
│                                  │                           │
│                                  ▼                           │
│         ┌────────────────────────────────────────┐          │
│         │          Supporting Services           │          │
│         ├────────────────┬──────────────────────┤          │
│         │   Kafka        │   Neon PostgreSQL    │          │
│         │   (Strimzi)    │   (External)         │          │
│         │   Event Stream │   Database           │          │
│         └────────────────┴──────────────────────┘          │
└──────────────────────────────────────────────────────────────┘
```

---

## 📊 Technology Stack

### Application Stack
| Component | Technology | Port |
|-----------|------------|------|
| **Frontend** | Next.js 14 + TypeScript | 3000 |
| **Backend** | FastAPI + SQLModel | 7860 |
| **Database** | Neon PostgreSQL | External |
| **Event Bus** | Apache Kafka | 9092 |
| **Runtime** | Dapr | 3500/50001 |

### Infrastructure Stack
| Component | Purpose |
|-----------|---------|
| **Docker** | Containerization |
| **Kubernetes** | Orchestration |
| **Dapr** | Microservices runtime |
| **Strimzi** | Kafka operator |
| **Oracle OKE** | Cloud K8s (Always Free) |

---

## 🎯 Deployment Comparison

| Feature | Docker Compose | Minikube | Oracle OKE |
|---------|---------------|----------|------------|
| **Use Case** | Local dev | K8s testing | Production |
| **Cost** | Free | Free | Always Free |
| **Setup Time** | 5 min | 15 min | 30 min |
| **Dapr Support** | ❌ | ✅ | ✅ |
| **Kafka** | Single node | Single node | Cluster |
| **Scalability** | None | Limited | Full |
| **High Availability** | No | No | Yes |

---

## 📁 File Reference

### Build & Run
```bash
# Build images
.\build-docker-images.ps1       # PowerShell
./build-docker-images.sh        # Bash

# Test locally
docker-compose up -d

# Deploy to K8s
kubectl apply -f k8s/
```

### Configuration Files
```yaml
k8s/namespace.yaml                           # Kubernetes namespace
k8s/backend-deployment.yaml                  # Backend deployment (port 7860)
k8s/frontend-deployment.yaml                 # Frontend deployment (port 3000)
k8s/kafka-cluster.yaml                       # Kafka cluster (Strimzi)
k8s/secrets.yaml                             # Database credentials
dapr/components/kubernetes-components.yaml   # Dapr components
docker-compose.yml                           # Local Docker setup
```

### Documentation
```
QUICK_DEPLOY.md                    # Quick start (START HERE)
DEPLOYMENT_SUMMARY.md              # Complete overview
DOCKER_BUILD_GUIDE.md              # Docker build details
KUBERNETES_DEPLOYMENT_GUIDE.md     # K8s + Oracle OKE
PHASE_V_DEPLOYMENT.md              # Original Phase-V guide
README.md                          # Project overview
```

---

## 🔧 Common Commands

### Docker Operations
```powershell
# Build
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

# Run
docker run -d -p 7860:7860 todo-backend:latest
docker run -d -p 3000:3000 todo-frontend:latest

# Test
curl http://localhost:7860/health
curl http://localhost:3000/health

# Logs
docker logs -f todo-backend
docker logs -f todo-frontend

# Clean
docker-compose down
docker system prune -f
```

### Kubernetes Operations
```powershell
# Deploy
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/backend-deployment.yaml -n todo-app
kubectl apply -f k8s/frontend-deployment.yaml -n todo-app

# Check status
kubectl get pods -n todo-app
kubectl get deployments -n todo-app
kubectl get svc -n todo-app

# Logs
kubectl logs -f deployment/todo-backend -n todo-app
kubectl logs -f deployment/todo-frontend -n todo-app

# Port forward
kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app

# Clean
kubectl delete namespace todo-app
```

---

## 🛠️ Troubleshooting

### Docker Build Issues

**Problem: Network errors**
```powershell
# Check Docker
docker info

# Restart Docker Desktop
# Retry build
```

**Problem: Port conflicts**
```powershell
# Find process using port
netstat -ano | findstr :3000

# Use different port
docker run -p 3001:3000 todo-frontend:latest
```

### Kubernetes Issues

**Problem: Pods not starting**
```powershell
# Check pod details
kubectl describe pod <pod-name> -n todo-app

# Check logs
kubectl logs <pod-name> -n todo-app
```

**Problem: Dapr not injected**
```powershell
# Check annotations
kubectl get pod <pod-name> -n todo-app -o yaml | grep dapr

# Re-annotate
kubectl annotate pod <pod-name> dapr.io/enabled=true --overwrite
```

---

## ✅ Pre-Deployment Checklist

### Before Building
- [ ] Docker Desktop running
- [ ] Internet connection stable
- [ ] ~3GB disk space available

### Before Kubernetes
- [ ] Images built successfully
- [ ] kubectl installed
- [ ] Cluster ready (Minikube/OKE)
- [ ] Dapr CLI installed

### Before Cloud (OKE)
- [ ] Oracle Cloud account
- [ ] OCI CLI configured
- [ ] OKE cluster created
- [ ] Images pushed to registry
- [ ] Database secrets set

---

## 📚 Documentation Guide

### Quick Reference
1. **QUICK_DEPLOY.md** - Start here for quick deployment
2. **DEPLOYMENT_SUMMARY.md** - Complete overview
3. **DOCKER_BUILD_GUIDE.md** - Docker details
4. **KUBERNETES_DEPLOYMENT_GUIDE.md** - K8s + Oracle OKE

### Detailed Reference
5. **PHASE_V_DEPLOYMENT.md** - Original Phase-V guide
6. **README.md** - Project overview
7. **k8s/*.yaml** - Kubernetes manifests
8. **dapr/components/*.yaml** - Dapr configs

---

## 🎉 Summary

Your Todo App Phase-V is now **fully configured** for:

✅ **Docker containerization** (frontend + backend)
✅ **Local testing** (Docker Compose)
✅ **Kubernetes deployment** (Minikube)
✅ **Cloud deployment** (Oracle OKE, Azure AKS)
✅ **Dapr integration** (pubsub, state, jobs)
✅ **Kafka event streaming** (Strimzi)
✅ **Complete documentation** (5 comprehensive guides)

**Choose your deployment target and go!** 🚀

---

**Questions?** Check `QUICK_DEPLOY.md` for step-by-step instructions.

**Last Updated:** 2026-03-14
**Project:** Todo App Phase-V
