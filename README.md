# Todo App Phase-V - Advanced Cloud Deployment

A production-grade, event-driven todo application with advanced features including recurring tasks, reminders, real-time sync, and cloud-native deployment.

## 🎯 Phase-V Features

### ✅ Event-Driven Architecture
- **Kafka** for event streaming
- **Dapr Pub/Sub** for abstraction
- Event sourcing for all task operations
- Real-time synchronization across clients

### ✅ Advanced Task Management
- **Recurring Tasks** - Smart detection and automatic generation
- **Reminders** - Exact-time scheduling with Dapr Jobs API
- **Priorities** - Low, Medium, High, Urgent
- **Tags** - Custom tags with colors
- **Search & Filter** - Advanced filtering and sorting

### ✅ Cloud-Native Deployment
- **Kubernetes** - Minikube local + Cloud (AKS/OKE/GKE)
- **Dapr** - Full integration (Pub/Sub, State, Jobs, Secrets)
- **CI/CD** - GitHub Actions pipeline
- **Monitoring** - Dapr Dashboard + Kubernetes logs

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         KUBERNETES CLUSTER                               │
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │   Frontend   │    │   Backend    │    │      KAFKA CLUSTER       │  │
│  │  Pod + Dapr  │───▶│  Pod + Dapr  │───▶│  ┌────────────────────┐  │  │
│  │  Next.js     │    │  FastAPI     │    │  │ todo-events        │  │  │
│  └──────────────┘    │  + MCP Tools │    │  │ reminders          │  │  │
│                      └──────┬───────┘    │  │ todo.recurring     │  │  │
│                             │            │  └─────────┬──────────┘  │  │
│                             │            └────────────┼─────────────┘  │
│                             │                         │                │
│                             ▼                         ▼                │
│                      ┌─────────────┐       ┌──────────────────────┐   │
│                      │  Neon DB    │       │ Recurring &          │   │
│                      │ (External)  │       │ Notification Services│   │
│                      └─────────────┘       └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop
- Minikube
- Dapr CLI
- kubectl
- Python 3.11
- Node.js 18+

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/todo-app-phase-V.git
cd todo-app-phase-V
```

### 2. Start Minikube

```bash
minikube start --cpus=4 --memory=4096
minikube addons enable ingress
```

### 3. Install Dapr

```bash
dapr init -k
```

### 4. Deploy Application

```bash
# Deploy namespace and components
kubectl apply -f k8s/namespace.yaml
kubectl apply -f dapr/components/kubernetes-components.yaml
kubectl apply -f k8s/secrets.yaml

# Deploy services
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

### 5. Access Application

```bash
# Get service URL
minikube service todo-frontend -n todo-app

# Or port forward
kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app
```

---

## 📁 Project Structure

```
todo-app-phase-V/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # REST API routes
│   │   ├── dapr/              # Dapr clients
│   │   ├── database/          # Database configuration
│   │   ├── events/            # Event publishing/consuming
│   │   ├── models/            # SQLModel models
│   │   ├── services/          # Business logic
│   │   └── workers/           # Background workers
│   └── main.py                # Application entry point
├── frontend/                   # Next.js frontend
│   └── src/
│       ├── components/        # React components
│       ├── pages/             # Next.js pages
│       └── types/             # TypeScript types
├── k8s/                        # Kubernetes manifests
│   ├── namespace.yaml
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── secrets.yaml
│   └── kafka-cluster.yaml
├── dapr/components/            # Dapr components
│   ├── pubsub.yaml
│   ├── statestore.yaml
│   ├── jobs.yaml
│   └── secrets.yaml
├── .github/workflows/          # CI/CD pipeline
│   └── ci-cd.yml
├── specs/                      # Specification documents
│   └── 005-phase-v-advanced-cloud/
├── PHASE_V_DEPLOYMENT.md       # Deployment guide
├── PHASE_V_IMPLEMENTATION_SUMMARY.md
└── README.md                   # This file
```

---

## 🔧 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLModel** - SQLAlchemy + Pydantic ORM
- **Neon PostgreSQL** - Serverless PostgreSQL
- **Kafka** - Event streaming
- **Dapr** - Distributed application runtime
- **Celery** - Background tasks (legacy, being replaced by Dapr Jobs)

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS
- **WebSocket** - Real-time updates

### Infrastructure
- **Kubernetes** - Container orchestration
- **Dapr** - Microservices runtime
- **Kafka/Strimzi** - Event streaming
- **GitHub Actions** - CI/CD
- **Docker** - Containerization

---

## 📋 API Endpoints

### Tasks
```
POST   /api/v1/todos/              # Create task
GET    /api/v1/todos/              # List tasks
GET    /api/v1/todos/{id}          # Get task
PUT    /api/v1/todos/{id}          # Update task
DELETE /api/v1/todos/{id}          # Delete task
PATCH  /api/v1/todos/{id}/toggle   # Toggle completion
```

### Recurring Tasks
```
POST   /api/v1/recurring/tasks/{id}     # Configure recurring
GET    /api/v1/recurring/tasks/{id}     # Get recurring config
PUT    /api/v1/recurring/tasks/{id}     # Update recurring
DELETE /api/v1/recurring/tasks/{id}     # Delete recurring
GET    /api/v1/recurring/               # List recurring tasks
```

### Reminders
```
POST   /api/v1/reminders/          # Create reminder
GET    /api/v1/reminders/          # List reminders
GET    /api/v1/reminders/{id}      # Get reminder
DELETE /api/v1/reminders/{id}     # Delete reminder
PUT    /api/v1/reminders/{id}      # Update reminder
```

### Dapr Jobs
```
POST   /api/jobs/trigger           # Job callback endpoint
```

---

## 🧪 Testing

### Test Recurring Tasks

```bash
# Create recurring task
curl -X POST "http://localhost:8001/api/v1/todos/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Pay electricity bill",
    "description": "Monthly utility payment",
    "priority": "high",
    "due_date": "2026-03-15T18:00:00Z"
  }'

# Complete task (triggers next instance)
curl -X PATCH "http://localhost:8001/api/v1/todos/TASK_ID/toggle" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Reminders

```bash
# Create reminder
curl -X POST "http://localhost:8001/api/v1/reminders/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "task_id": "TASK_UUID",
    "timing_minutes": 60,
    "delivery_channel": "email"
  }'
```

### Monitor Kafka Events

```bash
# Port forward to Kafka
kubectl port-forward svc/todo-kafka-kafka-bootstrap 9092:9092 -n todo-app

# Consume events
docker run --rm -it \
  -e BOOTSTRAP_SERVERS=host.docker.internal:9092 \
  confluentinc/cp-kafka:7.4.0 \
  kafka-console-consumer --bootstrap-server host.docker.internal:9092 \
  --topic todo-events --from-beginning
```

---

## ☁️ Cloud Deployment

### Azure AKS

```bash
# Create AKS cluster
az aks create --resource-group todo-app-rg --name todo-app-aks --node-count 2

# Get credentials
az aks get-credentials --resource-group todo-app-rg --name todo-app-aks

# Deploy
kubectl apply -f k8s/
```

### Oracle OKE (Always Free)

```bash
# Create OKE cluster via console
# Follow: https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengquickstart.htm

# Deploy
kubectl apply -f k8s/
```

See [PHASE_V_DEPLOYMENT.md](PHASE_V_DEPLOYMENT.md) for complete cloud deployment guide.

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

1. **Test** - Run pytest, linting, frontend build
2. **Build** - Build Docker images
3. **Push** - Push to GitHub Container Registry
4. **Deploy** - Deploy to Kubernetes

### Required Secrets

- `KUBE_CONFIG` - Base64-encoded kubeconfig
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub password/token

---

## 📊 Monitoring

### Dapr Dashboard

```bash
kubectl port-forward svc/dapr-dashboard 8080:8080 -n dapr-system
# Visit http://localhost:8080
```

### Kubernetes Logs

```bash
# Backend logs
kubectl logs -f deployment/todo-backend -n todo-app

# Dapr sidecar logs
kubectl logs -f deployment/todo-backend -c daprd -n todo-app
```

---

## 📚 Documentation

- **[PHASE_V_DEPLOYMENT.md](PHASE_V_DEPLOYMENT.md)** - Complete deployment guide
- **[PHASE_V_IMPLEMENTATION_SUMMARY.md](PHASE_V_IMPLEMENTATION_SUMMARY.md)** - Implementation details
- **[specs/005-phase-v-advanced-cloud/](specs/005-phase-v-advanced-cloud/)** - Requirements specification

---

## ✅ Phase-V Compliance Checklist

| Requirement | Status |
|-------------|--------|
| Recurring Tasks | ✅ Implemented |
| Reminders | ✅ Implemented |
| Kafka Event Publishing | ✅ Implemented |
| Dapr Pub/Sub | ✅ Implemented |
| Dapr State | ✅ Implemented |
| Dapr Jobs | ✅ Implemented |
| Dapr Secrets | ✅ Implemented |
| Minikube Deployment | ✅ Implemented |
| Cloud Deployment | ✅ Documented |
| CI/CD Pipeline | ✅ Implemented |
| Monitoring | ✅ Implemented |

---

## 🎯 Hackathon Submission

### Repository Contents

- ✅ All source code (backend + frontend)
- ✅ `/specs` folder with specification files
- ✅ Kubernetes manifests
- ✅ Dapr components
- ✅ CI/CD pipeline
- ✅ Comprehensive documentation

### Demo Video Outline (90 seconds)

1. **0-15s:** Show frontend UI, create task
2. **15-30s:** Demonstrate recurring task detection
3. **30-45s:** Set reminder, show Dapr Jobs scheduling
4. **45-60s:** Complete task, show next instance generated
5. **60-75s:** Show Kafka events in real-time
6. **75-90s:** Show Dapr Dashboard, Kubernetes pods

---

## 🤝 Contributing

This is a hackathon project. For questions or issues, please contact the repository owner.

---

## 📝 License

MIT License - See LICENSE file for details.

---

## 🎉 Summary

Your Phase-V implementation includes:

✅ **Event-Driven Architecture** with Kafka + Dapr Pub/Sub
✅ **Recurring Tasks** triggered by completion events
✅ **Reminders** scheduled with Dapr Jobs API (exact-time)
✅ **Full Dapr Integration** (Pub/Sub, State, Jobs, Secrets)
✅ **Kubernetes Deployment** (Minikube + Cloud)
✅ **CI/CD Pipeline** with GitHub Actions
✅ **Monitoring** via Dapr Dashboard + K8s logs

**Ready for production deployment!** 🚀
