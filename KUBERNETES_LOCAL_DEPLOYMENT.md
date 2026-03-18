# Kubernetes Local Deployment Guide
# Minikube + Dapr + Kafka + Helm

This guide walks you through deploying the Todo App locally using Minikube, Kubernetes, Dapr, and Kafka.

## 📋 Prerequisites

### Required Software
1. **Docker Desktop** or compatible container runtime
   - [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Ensure Docker is running before starting

2. **Minikube** - Local Kubernetes cluster
   - [Installation Guide](https://minikube.sigs.k8s.io/docs/start/)
   - Windows: `choco install minikube` or download from website
   - macOS: `brew install minikube`
   - Linux: Follow official documentation

3. **kubectl** - Kubernetes CLI
   - [Download kubectl](https://kubernetes.io/docs/tasks/tools/)
   - Verify: `kubectl version --client`

4. **Helm** - Kubernetes package manager
   - [Install Helm](https://helm.sh/docs/intro/install/)
   - Windows: `choco install kubernetes-helm`
   - macOS: `brew install helm`
   - Verify: `helm version`

5. **Dapr CLI** - Distributed application runtime
   - [Install Dapr](https://docs.dapr.io/getting-started/install-dapr-cli/)
   - Windows: `powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"`
   - macOS/Linux: `curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash`
   - Verify: `dapr --version`

### Optional Tools
- **Visual Studio Code** with Kubernetes extensions
- **k9s** - Terminal UI for Kubernetes
- **Lens** - Kubernetes dashboard

---

## 🚀 Quick Start

### Step 1: Setup Minikube

#### Windows (PowerShell)
```powershell
.\k8s\scripts\setup-minikube.ps1
```

#### Linux/macOS (Bash)
```bash
chmod +x k8s/scripts/setup-minikube.sh
./k8s/scripts/setup-minikube.sh
```

This script will:
- ✅ Check all prerequisites
- ✅ Start Minikube with optimal settings (4 CPUs, 8GB RAM, 20GB disk)
- ✅ Enable ingress and metrics-server addons
- ✅ Install Dapr on Kubernetes
- ✅ Verify all components are running

**Manual Setup (if script fails):**
```bash
# Start Minikube
minikube start --cpus=4 --memory=8192 --disk-size=20gb --driver=docker

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Install Dapr
dapr init -k --wait
```

---

### Step 2: Build Docker Images

Build your application images:

```bash
# Build all images
docker-compose build

# Or build individually
docker-compose build backend
docker-compose build frontend
```

---

### Step 3: Load Images into Minikube

```bash
# Load backend image
minikube image load todo-app-phase-v-backend:latest

# Load frontend image
minikube image load todo-app-phase-v-frontend:latest

# Verify images
minikube image list
```

---

### Step 4: Deploy to Kubernetes

#### Windows (PowerShell)
```powershell
# Set environment variables
$env:DATABASE_URL="your-database-url"
$env:OPENROUTER_API_KEY="your-api-key"
$env:JWT_SECRET="your-jwt-secret"

# Deploy
.\k8s\scripts\deploy-to-k8s.ps1
```

#### Linux/macOS (Bash)
```bash
# Set environment variables
export DATABASE_URL="your-database-url"
export OPENROUTER_API_KEY="your-api-key"
export JWT_SECRET="your-jwt-secret"

# Deploy
chmod +x k8s/scripts/deploy-to-k8s.sh
./k8s/scripts/deploy-to-k8s.sh
```

**Manual Deployment:**

```bash
# Create namespace
kubectl create namespace todo-app

# Deploy infrastructure (Kafka, Zookeeper, Redis)
helm upgrade --install infrastructure ./k8s/helm/infrastructure \
  --namespace todo-app \
  --create-namespace \
  --wait

# Apply Dapr components
kubectl apply -f k8s/manifests/dapr/ -n todo-app

# Deploy backend
helm upgrade --install todo-backend ./k8s/helm/backend \
  --namespace todo-app \
  --set image.repository=todo-app-phase-v-backend \
  --set image.tag=latest \
  --set env.DATABASE_URL="your-database-url" \
  --set env.OPENROUTER_API_KEY="your-api-key" \
  --wait

# Deploy frontend
helm upgrade --install todo-frontend ./k8s/helm/frontend \
  --namespace todo-app \
  --set image.repository=todo-app-phase-v-frontend \
  --set image.tag=latest \
  --wait
```

---

## 🔍 Verify Deployment

### Check Pods Status
```bash
kubectl get pods -n todo-app
```

Expected output:
```
NAME                            READY   STATUS    RESTARTS   AGE
kafka-xxxxxxxxx-xxxxx           1/1     Running   0          2m
redis-xxxxxxxxx-xxxxx           1/1     Running   0          2m
zookeeper-xxxxxxxxx-xxxxx       1/1     Running   0          2m
todo-backend-xxxxxxxxx-xxxxx    1/1     Running   0          1m
todo-frontend-xxxxxxxxx-xxxxx   1/1     Running   0          1m
```

### Check Services
```bash
kubectl get services -n todo-app
```

### Check Dapr Components
```bash
kubectl get components -n todo-app
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

---

## 🌐 Access Your Application

### Method 1: Port Forwarding (Recommended for Development)

```bash
# Port forward backend
kubectl port-forward -n todo-app svc/todo-backend 7860:7860

# In a new terminal, port forward frontend
kubectl port-forward -n todo-app svc/todo-frontend 3000:3000
```

Access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:7860
- **API Docs**: http://localhost:7860/docs

### Method 2: Ingress

1. Add to your hosts file:

**Windows** (Admin PowerShell):
```powershell
Add-Content -Path "C:\Windows\System32\drivers\etc\hosts" -Value "127.0.0.1 todo.local"
```

**Linux/macOS**:
```bash
sudo echo "127.0.0.1 todo.local" >> /etc/hosts
```

2. Access:
   - **Frontend**: http://todo.local
   - **Backend**: http://todo.local/api

### Method 3: Minikube Tunnel

```bash
# Start tunnel in background
minikube tunnel -p todo-app

# Get external IP
kubectl get services -n todo-app
```

---

## 🛠️ Management Commands

### Scale Applications
```bash
# Scale backend to 3 replicas
kubectl scale deployment -n todo-app todo-backend --replicas=3

# Scale frontend to 2 replicas
kubectl scale deployment -n todo-app todo-frontend --replicas=2
```

### Update Deployment
```bash
# Rebuild and reload images
docker-compose build
minikube image load todo-app-phase-v-backend:latest
minikube image load todo-app-phase-v-frontend:latest

# Restart deployments
kubectl rollout restart deployment -n todo-app todo-backend
kubectl rollout restart deployment -n todo-app todo-frontend
```

### View Dapr Dashboard
```bash
dapr dashboard -k
```

### View Kubernetes Dashboard
```bash
minikube dashboard -p todo-app
```

---

## 🧪 Testing

### Test Backend Health
```bash
curl http://localhost:7860/health
```

### Test Frontend
```bash
curl http://localhost:3000/health
```

### Test Dapr Integration
```bash
# Invoke backend through Dapr
dapr invoke -n todo-app -a todo-backend -m health -p http
```

---

## 🗑️ Cleanup

### Uninstall Application
```bash
# Remove Helm releases
helm uninstall todo-backend -n todo-app
helm uninstall todo-frontend -n todo-app
helm uninstall infrastructure -n todo-app

# Delete namespace
kubectl delete namespace todo-app

# Remove Dapr components
kubectl delete -f k8s/manifests/dapr/
```

### Stop Minikube
```bash
minikube stop -p todo-app
```

### Delete Minikube Cluster
```bash
minikube delete -p todo-app
```

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Minikube Cluster                     │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │              todo-app Namespace                     │ │
│  │                                                     │ │
│  │  ┌──────────────┐    ┌──────────────┐             │ │
│  │  │   Frontend   │───▶│    Backend   │             │ │
│  │  │  (Next.js)   │    │   (FastAPI)  │             │ │
│  │  │   :3000      │    │    :7860     │             │ │
│  │  └──────────────┘    └──────┬───────┘             │ │
│  │         │                   │                       │ │
│  │         │              ┌────┴────┐                 │ │
│  │         │              │  Dapr   │                 │ │
│  │         │              │ Sidecar │                 │ │
│  │         │              └────┬────┘                 │ │
│  │         │                   │                       │ │
│  │         │          ┌────────┼────────┐             │ │
│  │         │          │        │        │             │ │
│  │         ▼          ▼        ▼        ▼             │ │
│  │                                    ┌────────────┐  │ │
│  │                                    │   Kafka    │  │ │
│  │                                    │  :9092     │  │ │
│  │                                    └────────────┘  │ │
│  │                                    ┌────────────┐  │ │
│  │                                    │   Redis    │  │ │
│  │                                    │  :6379     │  │ │
│  │                                    └────────────┘  │ │
│  │                                    ┌────────────┐  │ │
│  │                                    │ Zookeeper  │  │ │
│  │                                    │  :2181     │  │ │
│  │                                    └────────────┘  │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Pods Not Starting
```bash
# Check pod status
kubectl describe pod -n todo-app <pod-name>

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

### Image Pull Errors
```bash
# Verify image is loaded
minikube image list | grep todo-app

# Reload image
minikube image load todo-app-phase-v-backend:latest
```

### Dapr Issues
```bash
# Check Dapr sidecar injection
kubectl get pods -n todo-app -o jsonpath='{.items[*].metadata.annotations.dapr\.io\/app-id}'

# Check Dapr components
kubectl get components -n todo-app -o yaml
```

### Resource Issues
```bash
# Increase Minikube resources
minikube stop
minikube start --cpus=6 --memory=16384 -p todo-app
```

---

## 📝 Configuration Reference

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Neon PostgreSQL connection string | Required |
| `JWT_SECRET` | JWT signing secret | Required |
| `OPENROUTER_API_KEY` | OpenRouter API key | Required |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka brokers | kafka:29092 |
| `CELERY_BROKER_URL` | Redis broker URL | redis://redis:6379/0 |
| `SMTP_USERNAME` | SMTP username | Optional |
| `SMTP_PASSWORD` | SMTP password | Optional |

### Helm Values

See individual `values.yaml` files:
- `k8s/helm/backend/values.yaml`
- `k8s/helm/frontend/values.yaml`
- `k8s/helm/infrastructure/values.yaml`

---

## 🎯 Next Steps: Deploy to Oracle Cloud

After testing locally, deploy to Oracle Cloud Infrastructure (OCI):

1. **Create Oracle Kubernetes Engine (OKE) cluster**
2. **Set up OCI Container Registry**
3. **Push Docker images to OCI Registry**
4. **Configure load balancer**
5. **Set up external database**
6. **Configure ingress with TLS**

See `KUBERNETES_ORACLE_DEPLOYMENT.md` for detailed instructions.

---

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Dapr Documentation](https://docs.dapr.io/)
- [Helm Documentation](https://helm.sh/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Kafka on Kubernetes](https://kafka.apache.org/)

---

## 🆘 Support

For issues or questions:
- Check logs: `kubectl logs -n todo-app <pod-name>`
- Describe resources: `kubectl describe -n todo-app <resource-name>`
- Review Dapr logs: `kubectl logs -n todo-app <pod-name> -c daprd`

---

**Last Updated:** 2026-03-18  
**Author:** Naseer Ahmed
