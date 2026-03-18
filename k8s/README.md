# Kubernetes Deployment for Todo App Phase V

This directory contains all Kubernetes manifests, Helm charts, and deployment scripts for deploying the Todo App to Kubernetes.

## 📁 Directory Structure

```
k8s/
├── helm/                          # Helm Charts
│   ├── backend/                   # Backend Helm chart
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       └── _helpers.tpl
│   ├── frontend/                  # Frontend Helm chart
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       └── _helpers.tpl
│   └── infrastructure/            # Infrastructure Helm chart
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── kafka.yaml
│           ├── zookeeper.yaml
│           └── redis.yaml
│
├── manifests/                     # Kubernetes Manifests
│   ├── base/                      # Base configurations
│   └── dapr/                      # Dapr Components
│       ├── redis-statestore.yaml
│       ├── kafka-pubsub.yaml
│       └── secretstore.yaml
│
└── scripts/                       # Deployment Scripts
    ├── setup-minikube.sh          # Minikube setup (Linux/macOS)
    ├── setup-minikube.ps1         # Minikube setup (Windows)
    ├── deploy-to-k8s.sh           # Deploy to K8s (Linux/macOS)
    └── deploy-to-k8s.ps1          # Deploy to K8s (Windows)
```

## 🚀 Quick Start

### 1. Setup Minikube (Local Development)

**Windows:**
```powershell
.\k8s\scripts\setup-minikube.ps1
```

**Linux/macOS:**
```bash
chmod +x k8s/scripts/setup-minikube.sh
./k8s/scripts/setup-minikube.sh
```

### 2. Deploy Application

**Windows:**
```powershell
$env:DATABASE_URL="your-database-url"
$env:OPENROUTER_API_KEY="your-api-key"
.\k8s\scripts\deploy-to-k8s.ps1
```

**Linux/macOS:**
```bash
export DATABASE_URL="your-database-url"
export OPENROUTER_API_KEY="your-api-key"
chmod +x k8s/scripts/deploy-to-k8s.sh
./k8s/scripts/deploy-to-k8s.sh
```

## 📚 Documentation

- **Local Deployment**: See `KUBERNETES_LOCAL_DEPLOYMENT.md` in root directory
- **Oracle Cloud Deployment**: See `KUBERNETES_ORACLE_DEPLOYMENT.md` in root directory

## 🛠️ Components

### Infrastructure
- **Kafka** - Message broker for event streaming
- **Zookeeper** - Kafka coordination
- **Redis** - State store and cache

### Dapr Components
- **statestore** - Redis-based state management
- **messagebus** - Kafka-based pub/sub
- **secretstore** - Kubernetes secrets integration

### Applications
- **todo-backend** - FastAPI backend with Dapr sidecar
- **todo-frontend** - Next.js frontend with Dapr sidecar

## 🔧 Manual Deployment

### Install Infrastructure

```bash
kubectl create namespace todo-app

helm upgrade --install infrastructure ./k8s/helm/infrastructure \
  --namespace todo-app \
  --create-namespace \
  --wait
```

### Apply Dapr Components

```bash
kubectl apply -f k8s/manifests/dapr/ -n todo-app
```

### Deploy Backend

```bash
helm upgrade --install todo-backend ./k8s/helm/backend \
  --namespace todo-app \
  --set env.DATABASE_URL="your-database-url" \
  --set env.OPENROUTER_API_KEY="your-api-key" \
  --wait
```

### Deploy Frontend

```bash
helm upgrade --install todo-frontend ./k8s/helm/frontend \
  --namespace todo-app \
  --wait
```

## ✅ Verify Deployment

```bash
# Check pods
kubectl get pods -n todo-app

# Check services
kubectl get services -n todo-app

# Check Dapr components
kubectl get components -n todo-app

# View logs
kubectl logs -n todo-app -l app.kubernetes.io/name=todo-backend -f
```

## 🌐 Access Application

```bash
# Port forward backend
kubectl port-forward -n todo-app svc/todo-backend 7860:7860

# Port forward frontend
kubectl port-forward -n todo-app svc/todo-frontend 3000:3000
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:7860

## 🗑️ Cleanup

```bash
# Remove all deployments
helm uninstall todo-backend -n todo-app
helm uninstall todo-frontend -n todo-app
helm uninstall infrastructure -n todo-app

# Delete namespace
kubectl delete namespace todo-app
```

## 📝 Configuration

### Environment Variables

Set these before deployment:

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Neon PostgreSQL URL | ✅ |
| `JWT_SECRET` | JWT signing secret | ✅ |
| `OPENROUTER_API_KEY` | OpenRouter API key | ✅ |
| `SMTP_USERNAME` | SMTP username | ❌ |
| `SMTP_PASSWORD` | SMTP password | ❌ |
| `FROM_EMAIL` | From email address | ❌ |

### Helm Values

Customize deployment by modifying `values.yaml` files or using `--set` flags:

```bash
helm upgrade --install todo-backend ./k8s/helm/backend \
  --set replicaCount=3 \
  --set resources.limits.memory=2Gi \
  --set env.DATABASE_URL="..."
```

## 🎯 Production Considerations

For production deployment on Oracle Cloud:

1. Use Oracle Container Registry (OCIR) for images
2. Configure Load Balancer with proper SSL/TLS
3. Set up external database (Neon PostgreSQL)
4. Enable horizontal pod autoscaling
5. Configure proper resource limits
6. Set up monitoring and alerting
7. Use Kubernetes secrets for sensitive data

See `KUBERNETES_ORACLE_DEPLOYMENT.md` for detailed instructions.

## 🆘 Troubleshooting

### Common Issues

**Pods not starting:**
```bash
kubectl describe pod -n todo-app <pod-name>
kubectl logs -n todo-app <pod-name>
```

**Dapr sidecar issues:**
```bash
kubectl logs -n todo-app <pod-name> -c daprd
dapr status -k
```

**Image pull errors:**
```bash
kubectl create secret docker-registry ocir-secret \
  --docker-server=<REGION>.ocir.io \
  --docker-username='<USERNAME>' \
  --docker-password='<TOKEN>' \
  -n todo-app
```

## 📞 Support

For issues or questions, check:
- Kubernetes logs: `kubectl logs -n todo-app <pod-name>`
- Dapr dashboard: `dapr dashboard -k`
- Minikube dashboard: `minikube dashboard`

---

**Version:** 1.0.0  
**Last Updated:** 2026-03-18  
**Author:** Naseer Ahmed
