# 🎉 Kubernetes Deployment Complete!

## ✅ What's Been Created

Your Todo App is now ready for local Kubernetes deployment with Minikube, Dapr, and Kafka, and prepared for Oracle Cloud deployment.

---

## 📁 Files Created

### Helm Charts (`k8s/helm/`)
```
k8s/helm/
├── backend/
│   ├── Chart.yaml              # Backend chart metadata
│   ├── values.yaml             # Backend configuration
│   └── templates/
│       ├── deployment.yaml     # Backend deployment + service
│       └── _helpers.tpl        # Helm helper functions
│
├── frontend/
│   ├── Chart.yaml              # Frontend chart metadata
│   ├── values.yaml             # Frontend configuration
│   └── templates/
│       ├── deployment.yaml     # Frontend deployment + ingress
│       └── _helpers.tpl        # Helm helper functions
│
└── infrastructure/
    ├── Chart.yaml              # Infrastructure chart metadata
    ├── values.yaml             # Kafka, Redis, Zookeeper config
    └── templates/
        ├── kafka.yaml          # Kafka deployment + service
        ├── zookeeper.yaml      # Zookeeper deployment + service
        └── redis.yaml          # Redis deployment + service
```

### Kubernetes Manifests (`k8s/manifests/`)
```
k8s/manifests/dapr/
├── redis-statestore.yaml       # Dapr state store (Redis)
├── kafka-pubsub.yaml           # Dapr pub/sub (Kafka)
└── secretstore.yaml            # Dapr secret store (K8s)
```

### Deployment Scripts (`k8s/scripts/`)
```
k8s/scripts/
├── setup-minikube.sh           # Minikube setup (Linux/macOS)
├── setup-minikube.ps1          # Minikube setup (Windows)
├── deploy-to-k8s.sh            # Deploy app (Linux/macOS)
└── deploy-to-k8s.ps1           # Deploy app (Windows)
```

### Documentation
```
├── KUBERNETES_LOCAL_DEPLOYMENT.md      # Local deployment guide
├── KUBERNETES_ORACLE_DEPLOYMENT.md     # Oracle Cloud guide
└── k8s/README.md                       # Quick reference
```

---

## 🚀 Quick Start Guide

### Step 1: Install Prerequisites

**Required:**
- Docker Desktop
- Minikube
- kubectl
- Helm
- Dapr CLI

**Install on Windows:**
```powershell
# Using Chocolatey
choco install minikube kubernetes-helm kubernetes-cli

# Install Dapr CLI
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

**Install on Linux/macOS:**
```bash
# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Dapr CLI
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash
```

### Step 2: Setup Minikube

**Windows:**
```powershell
.\k8s\scripts\setup-minikube.ps1
```

**Linux/macOS:**
```bash
chmod +x k8s/scripts/setup-minikube.sh
./k8s/scripts/setup-minikube.sh
```

### Step 3: Build and Load Images

```bash
# Build Docker images
docker-compose build backend
docker-compose build frontend

# Load into Minikube
minikube image load todo-app-phase-v-backend:latest
minikube image load todo-app-phase-v-frontend:latest
```

### Step 4: Deploy Application

**Windows:**
```powershell
$env:DATABASE_URL="your-neon-db-url"
$env:OPENROUTER_API_KEY="your-api-key"
$env:JWT_SECRET="your-secret"
.\k8s\scripts\deploy-to-k8s.ps1
```

**Linux/macOS:**
```bash
export DATABASE_URL="your-neon-db-url"
export OPENROUTER_API_KEY="your-api-key"
export JWT_SECRET="your-secret"
chmod +x k8s/scripts/deploy-to-k8s.sh
./k8s/scripts/deploy-to-k8s.sh
```

### Step 5: Access Application

```bash
# Port forward services
kubectl port-forward -n todo-app svc/todo-frontend 3000:3000
kubectl port-forward -n todo-app svc/todo-backend 7860:7860
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:7860
- API Docs: http://localhost:7860/docs

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Minikube Cluster                    │
│                                                       │
│  ┌───────────────────────────────────────────────┐  │
│  │            todo-app Namespace                  │  │
│  │                                                │  │
│  │  ┌──────────────┐      ┌──────────────┐      │  │
│  │  │   Frontend   │─────▶│    Backend   │      │  │
│  │  │  (Next.js)   │      │   (FastAPI)  │      │  │
│  │  │   :3000      │      │    :7860     │      │  │
│  │  └──────────────┘      └──────┬───────┘      │  │
│  │         │                     │               │  │
│  │         │                ┌────┴────┐          │  │
│  │         │                │ Dapr    │          │  │
│  │         │                │ Sidecar │          │  │
│  │         │                └────┬────┘          │  │
│  │         │                     │               │  │
│  │         │          ┌──────────┼──────────┐    │  │
│  │         │          │          │          │    │  │
│  │         ▼          ▼          ▼          ▼    │  │
│  │  ┌──────────┐ ┌────────┐ ┌────────┐        │  │
│  │  │  Kafka   │ │ Redis  │ │ZooKeeper│       │  │
│  │  │ :9092    │ │ :6379  │ │ :2181   │       │  │
│  │  └──────────┘ └────────┘ └────────┘        │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Components Overview

### Infrastructure
| Component | Purpose | Port |
|-----------|---------|------|
| **Kafka** | Event streaming, task events | 9092 |
| **Zookeeper** | Kafka coordination | 2181 |
| **Redis** | State store, cache, Celery broker | 6379 |

### Dapr Components
| Component | Type | Purpose |
|-----------|------|---------|
| **statestore** | state.redis | Store user preferences, task state |
| **messagebus** | pubsub.kafka | Event-driven architecture |
| **secretstore** | secretstores.kubernetes | Secure secrets management |

### Applications
| Application | Replicas | Port | Dapr App ID |
|-------------|----------|------|-------------|
| **todo-backend** | 1 | 7860 | todo-backend |
| **todo-frontend** | 1 | 3000 | todo-frontend |

---

## 🔧 Management Commands

### View Status
```bash
# Check pods
kubectl get pods -n todo-app

# Check services
kubectl get services -n todo-app

# Check Dapr components
kubectl get components -n todo-app

# View Dapr dashboard
dapr dashboard -k
```

### Scale Applications
```bash
# Scale backend
kubectl scale deployment -n todo-app todo-backend --replicas=3

# Scale frontend
kubectl scale deployment -n todo-app todo-frontend --replicas=2
```

### View Logs
```bash
# Backend logs
kubectl logs -n todo-app -l app.kubernetes.io/name=todo-backend -f

# Frontend logs
kubectl logs -n todo-app -l app.kubernetes.io/name=todo-frontend -f

# Kafka logs
kubectl logs -n todo-app -l app=kafka -f
```

### Update Deployment
```bash
# Rebuild and reload
docker-compose build
minikube image load todo-app-phase-v-backend:latest
minikube image load todo-app-phase-v-frontend:latest

# Restart
kubectl rollout restart deployment -n todo-app todo-backend
kubectl rollout restart deployment -n todo-app todo-frontend
```

---

## 🗑️ Cleanup

### Remove Application Only
```bash
helm uninstall todo-backend -n todo-app
helm uninstall todo-frontend -n todo-app
helm uninstall infrastructure -n todo-app
kubectl delete namespace todo-app
```

### Remove Everything
```bash
# Delete Minikube cluster
minikube delete -p todo-app
```

---

## 🎯 Next Steps: Deploy to Oracle Cloud

After testing locally, deploy to Oracle Cloud Infrastructure:

1. **Create OKE Cluster** in OCI Console
2. **Create Container Registry** and push images
3. **Configure kubectl** for OKE
4. **Install Dapr** on OKE
5. **Deploy with Helm** using OCI registry images
6. **Configure Load Balancer** and DNS
7. **Enable SSL/TLS** with cert-manager

📖 **See:** `KUBERNETES_ORACLE_DEPLOYMENT.md` for detailed instructions.

---

## 📝 Environment Variables

Configure these before deployment:

```bash
# Required
export DATABASE_URL="postgresql://..."
export OPENROUTER_API_KEY="sk-or-..."
export JWT_SECRET="your-secret-key"

# Optional (Email)
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
export FROM_EMAIL="your-email@gmail.com"
```

---

## 🆘 Troubleshooting

### Pods Not Starting
```bash
# Check pod details
kubectl describe pod -n todo-app <pod-name>

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

### Dapr Issues
```bash
# Check Dapr status
dapr status -k

# Check sidecar logs
kubectl logs -n todo-app <pod-name> -c daprd
```

### Image Pull Errors
```bash
# Verify image is loaded
minikube image list | grep todo-app

# Reload image
minikube image load todo-app-phase-v-backend:latest
```

### Resource Issues
```bash
# Increase Minikube resources
minikube stop
minikube start --cpus=6 --memory=16384 -p todo-app
```

---

## 📚 Documentation Links

- **Local Deployment Guide**: `KUBERNETES_LOCAL_DEPLOYMENT.md`
- **Oracle Cloud Guide**: `KUBERNETES_ORACLE_DEPLOYMENT.md`
- **k8s README**: `k8s/README.md`

---

## ✅ Success Checklist

- [ ] Minikube cluster running
- [ ] Dapr installed on Kubernetes
- [ ] Kafka, Zookeeper, Redis deployed
- [ ] Backend deployed with Dapr sidecar
- [ ] Frontend deployed with Dapr sidecar
- [ ] All pods healthy and running
- [ ] Can access frontend at http://localhost:3000
- [ ] Can access backend API at http://localhost:7860
- [ ] Dapr components configured correctly

---

**🎉 Congratulations!** Your Todo App is now running on Kubernetes with Dapr and Kafka!

---

**Version:** 1.0.0  
**Last Updated:** 2026-03-18  
**Author:** Naseer Ahmed
