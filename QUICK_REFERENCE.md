# Phase-V Quick Reference Card

## 🚀 Quick Start Commands

### Start Local Environment
```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=4096

# 2. Install Dapr
dapr init -k

# 3. Verify
kubectl get pods -n dapr-system
dapr status -k
```

### Deploy Application
```bash
# Deploy everything
kubectl apply -f k8s/namespace.yaml
kubectl apply -f dapr/components/kubernetes-components.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# Check status
kubectl get pods -n todo-app
```

### Access Application
```bash
# Get URL
minikube service todo-frontend -n todo-app

# Or port forward
kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app
```

---

## 📝 API Quick Reference

### Create Task
```bash
curl -X POST "http://localhost:8001/api/v1/todos/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Pay electricity bill",
    "description": "Monthly utility payment",
    "priority": "high",
    "due_date": "2026-03-15T18:00:00Z"
  }'
```

### Create Reminder
```bash
curl -X POST "http://localhost:8001/api/v1/reminders/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "task_id": "TASK_UUID",
    "timing_minutes": 60,
    "delivery_channel": "email"
  }'
```

### Complete Task
```bash
curl -X PATCH "http://localhost:8001/api/v1/todos/TASK_ID/toggle" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔍 Monitoring Commands

### Check Pods
```bash
kubectl get pods -n todo-app
```

### Check Dapr Components
```bash
kubectl get components.dapr.io -n todo-app
```

### View Logs
```bash
# Backend
kubectl logs -f deployment/todo-backend -n todo-app

# Dapr sidecar
kubectl logs -f deployment/todo-backend -c daprd -n todo-app
```

### Dapr Dashboard
```bash
kubectl port-forward svc/dapr-dashboard 8080:8080 -n dapr-system
# Visit http://localhost:8080
```

---

## 🧪 Testing Commands

### Monitor Kafka Events
```bash
# Port forward
kubectl port-forward svc/todo-kafka-kafka-bootstrap 9092:9092 -n todo-app

# Consume events
docker run --rm -it \
  -e BOOTSTRAP_SERVERS=host.docker.internal:9092 \
  confluentinc/cp-kafka:7.4.0 \
  kafka-console-consumer --bootstrap-server host.docker.internal:9092 \
  --topic todo-events --from-beginning
```

### Check Recurring Tasks
```bash
kubectl get pods -n todo-app
kubectl logs deployment/todo-backend -n todo-app | grep "recurring"
```

### Check Reminders
```bash
kubectl logs deployment/todo-backend -n todo-app | grep "reminder"
kubectl logs deployment/todo-backend -n todo-app | grep "job trigger"
```

---

## 🏗️ Architecture Components

| Component | Purpose | Port |
|-----------|---------|------|
| **Frontend** | Next.js UI | 3000 |
| **Backend** | FastAPI API | 8001 |
| **Kafka** | Event streaming | 9092 |
| **Dapr** | Sidecar runtime | 3500 (HTTP), 50001 (gRPC) |
| **Neon DB** | PostgreSQL | External |

---

## 📦 Docker Images

### Build Locally
```bash
# Backend
docker build -t todo-backend:latest ./backend

# Frontend
docker build -t todo-frontend:latest ./frontend

# Load into Minikube
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
```

---

## 🔧 Troubleshooting

### Pod Not Starting
```bash
kubectl describe pod <pod-name> -n todo-app
kubectl logs <pod-name> -n todo-app
```

### Dapr Sidecar Not Injected
```bash
kubectl get pod <pod-name> -n todo-app -o yaml | grep dapr
kubectl annotate pod <pod-name> dapr.io/enabled=true -n todo-app
```

### Kafka Connection Failed
```bash
kubectl get pods -n todo-app -l app.kubernetes.io/name=kafka
kubectl logs <kafka-pod> -n todo-app
```

### Reset Everything
```bash
# Delete namespace
kubectl delete namespace todo-app

# Restart Minikube
minikube delete
minikube start

# Reinstall Dapr
dapr init -k
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Main documentation |
| `PHASE_V_DEPLOYMENT.md` | Complete deployment guide |
| `PHASE_V_IMPLEMENTATION_SUMMARY.md` | Implementation details |
| `PHASE_V_HACKATHON_SUMMARY.md` | Hackathon submission guide |
| `specs/005-phase-v-advanced-cloud/001-phase-v-requirements.spec.md` | Requirements |

---

## ✅ Pre-Submission Checklist

- [ ] Minikube running
- [ ] Dapr installed
- [ ] Application deployed
- [ ] All pods healthy
- [ ] Can create tasks
- [ ] Can set reminders
- [ ] Recurring tasks working
- [ ] Kafka events publishing
- [ ] Dapr Dashboard accessible
- [ ] Demo video ready (90 seconds)

---

## 🎯 Demo Flow (90 seconds)

1. **0-15s:** Show frontend, create task
2. **15-30s:** Show recurring detection
3. **30-45s:** Set reminder, show Dapr Jobs
4. **45-60s:** Complete task, show next instance
5. **60-75s:** Show Kafka events
6. **75-90s:** Show Dapr Dashboard, K8s pods

---

## 🚨 Emergency Commands

### Everything Broken?
```bash
# Nuclear option
minikube delete
dapr uninstall -k

# Start fresh
minikube start
dapr init -k
kubectl apply -f k8s/
```

### Need Help?
```bash
# Check Dapr
dapr status -k

# Check Kubernetes
kubectl get all -n todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

---

**Good luck! 🚀**
