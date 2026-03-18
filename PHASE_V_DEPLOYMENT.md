# Phase-V: Advanced Cloud Deployment Guide

## Overview

This guide covers the complete deployment of the Todo App with advanced features including:
- ✅ **Event-Driven Architecture** with Kafka
- ✅ **Dapr Integration** (Pub/Sub, State, Jobs, Secrets)
- ✅ **Recurring Tasks** (event-driven generation)
- ✅ **Reminders** (Dapr Jobs API for exact-time scheduling)
- ✅ **Kubernetes Deployment** (Minikube & Cloud)
- ✅ **CI/CD Pipeline** (GitHub Actions)

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          KUBERNETES CLUSTER                                   │
│                                                                               │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────────────────┐    │
│  │  Frontend   │   │  Backend    │   │         KAFKA CLUSTER           │    │
│  │  Pod + Dapr │──▶│  Pod + Dapr │──▶│  ┌──────────┐  ┌────────────┐  │    │
│  └─────────────┘   │  + MCP      │   │  │task-events│  │ reminders │  │    │
│                    │  Tools      │   │  └──────────┘  └────────────┘  │    │
│                    └──────┬──────┘   └──────────┬──────────┬──────────┘    │
│                           │                     │          │                │
│                           ▼                     ▼          ▼                │
│                    ┌─────────────┐   ┌────────────────────────────────┐    │
│                    │   Neon DB   │   │  Recurring & Notification      │    │
│                    │  (External) │   │  Services (event-driven)       │    │
│                    └─────────────┘   └────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Part A: Local Deployment with Minikube

### Prerequisites

1. **Docker Desktop** installed and running
2. **Minikube** installed
3. **Dapr CLI** installed
4. **kubectl** installed
5. **Helm** installed (optional)

### Step 1: Install Minikube

```bash
# Windows (PowerShell)
choco install minikube

# Or download from: https://minikube.sigs.k8s.io/docs/start/
```

### Step 2: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=4096 --disk-size=20gb

# Enable ingress
minikube addons enable ingress

# Enable metrics server (optional for monitoring)
minikube addons enable metrics-server
```

### Step 3: Install Dapr on Kubernetes

```bash
# Initialize Dapr on Kubernetes
dapr init -k

# Verify Dapr installation
kubectl get pods -n dapr-system
```

Expected output:
```
NAME                                    READY   STATUS    RESTARTS   AGE
dapr-dashboard-xxx                      1/1     Running   0          2m
dapr-operator-xxx                       1/1     Running   0          2m
dapr-placement-server-0                 1/1     Running   0          2m
dapr-sentry-xxx                         1/1     Running   0          2m
dapr-sidecar-injector-xxx               1/1     Running   0          2m
```

### Step 4: Deploy Kafka (Strimzi Operator)

```bash
# Create namespace
kubectl create namespace todo-app

# Install Strimzi Operator
kubectl apply -f https://strimzi.io/install/latest?namespace=todo-app -n todo-app

# Wait for operator to be ready
kubectl wait --for=condition=Available deployment/strimzi-cluster-operator -n todo-app --timeout=300s

# Deploy Kafka cluster
kubectl apply -f k8s/kafka-cluster.yaml -n todo-app

# Verify Kafka is running
kubectl get pods -n todo-app -l app.kubernetes.io/name=kafka
```

### Step 5: Deploy Dapr Components

```bash
# Deploy Dapr components
kubectl apply -f dapr/components/kubernetes-components.yaml -n todo-app

# Deploy secrets
kubectl apply -f k8s/secrets.yaml -n todo-app

# Verify components
kubectl get components.dapr.io -n todo-app
```

Expected output:
```
NAME               AGE
kafka-pubsub       2m
statestore         2m
kubernetes-secrets 2m
```

### Step 6: Build and Load Docker Images

```bash
# Build backend image
docker build -t todo-backend:latest ./backend

# Build frontend image
docker build -t todo-frontend:latest ./frontend

# Load images into Minikube
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
```

### Step 7: Deploy Application

```bash
# Deploy backend
kubectl apply -f k8s/backend-deployment.yaml -n todo-app

# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml -n todo-app

# Verify deployments
kubectl get deployments -n todo-app
kubectl get pods -n todo-app
```

### Step 8: Access the Application

```bash
# Option 1: Port forwarding
kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app
kubectl port-forward svc/todo-backend 8001:8001 -n todo-app

# Option 2: Minikube service
minikube service todo-frontend -n todo-app

# Option 3: Get service URL
minikube service todo-frontend -n todo-app --url
```

### Step 9: Verify Dapr Sidecars

```bash
# Check Dapr sidecars are injected
kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.annotations.dapr\.io/app-id}{"\n"}{end}'

# Check Dapr status
dapr status -k
```

---

## Part B: Testing Recurring Tasks & Reminders

### Test 1: Create Recurring Task

```bash
# Create a task with recurring pattern
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

**Expected:**
- Task created with `is_recurring=true`
- Kafka event published to `task-events` topic
- Recurring configuration created

### Test 2: Verify Kafka Events

```bash
# Port forward to Kafka
kubectl port-forward svc/todo-kafka-kafka-bootstrap 9092:9092 -n todo-app

# Use Kafka console consumer to verify events
docker run --rm -it \
  -e BOOTSTRAP_SERVERS=host.docker.internal:9092 \
  confluentinc/cp-kafka:7.4.0 \
  kafka-console-consumer --bootstrap-server host.docker.internal:9092 \
  --topic todo-events --from-beginning
```

**Expected Output:**
```json
{
  "event_type": "task.created",
  "payload": {
    "task_id": "uuid",
    "task_data": {...},
    "is_recurring": true
  },
  "user_id": "uuid",
  "timestamp": "2026-02-19T10:00:00Z"
}
```

### Test 3: Create Reminder with Dapr Jobs API

```bash
# Create a reminder
curl -X POST "http://localhost:8001/api/v1/reminders/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "task_id": "TASK_UUID",
    "timing_minutes": 60,
    "delivery_channel": "email"
  }'
```

**Expected:**
- Reminder created
- Dapr Job scheduled at exact time
- Event published to `reminders` topic

### Test 4: Verify Dapr Jobs

```bash
# Check Dapr Jobs (requires Dapr dashboard)
kubectl port-forward svc/dapr-dashboard 8080:8080 -n dapr-system

# Visit http://localhost:8080
# Navigate to Components → dapr-jobs
```

### Test 5: Complete Task (Trigger Recurring)

```bash
# Mark task as completed
curl -X PATCH "http://localhost:8001/api/v1/todos/TASK_ID/toggle" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected:**
- Task marked as completed
- Kafka event `task.completed` published
- Recurring service consumes event
- Next instance generated automatically

---

## Part C: Cloud Deployment (Azure AKS)

### Step 1: Create Azure Account

- Sign up at https://azure.microsoft.com/en-us/free/
- $200 credits for 30 days

### Step 2: Install Azure CLI

```bash
# Windows
choco install azure-cli

# Or download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
```

### Step 3: Login to Azure

```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

### Step 4: Create AKS Cluster

```bash
# Create resource group
az group create --name todo-app-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group todo-app-rg \
  --name todo-app-aks \
  --node-count 2 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group todo-app-rg --name todo-app-aks

# Verify connection
kubectl get nodes
```

### Step 5: Install Dapr on AKS

```bash
dapr init -k
```

### Step 6: Deploy to AKS

```bash
# Update image registry (push to ACR or Docker Hub)
az acr create --resource-group todo-app-rg --name todoappacr --sku Basic
az acr login --name todoappacr

# Tag and push images
docker tag todo-backend:latest todoappacr.azurecr.io/todo-backend:latest
docker tag todo-frontend:latest todoappacr.azurecr.io/todo-frontend:latest
docker push todoappacr.azurecr.io/todo-backend:latest
docker push todoappacr.azurecr.io/todo-frontend:latest

# Update deployment YAML with new image names
# k8s/backend-deployment.yaml: image: todoappacr.azurecr.io/todo-backend:latest
# k8s/frontend-deployment.yaml: image: todoappacr.azurecr.io/todo-frontend:latest

# Deploy
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

### Step 7: Expose Service

```bash
# Create LoadBalancer service
kubectl expose deployment todo-frontend --type=LoadBalancer --port=80 --target-port=3000 -n todo-app

# Get external IP
kubectl get svc -n todo-app

# Wait for EXTERNAL-IP to be assigned (may take 2-5 minutes)
```

---

## Part D: Cloud Deployment (Oracle OKE - Always Free)

### Step 1: Create Oracle Cloud Account

- Sign up at https://www.oracle.com/cloud/free/
- Always free: 4 OCPUs, 24GB RAM

### Step 2: Install OCI CLI

```bash
# Windows
choco install oracle-oci-cli
```

### Step 3: Create OKE Cluster

```bash
# Configure OCI CLI
oci setup config

# Create cluster via console or CLI
# Follow: https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengquickstart.htm
```

### Step 4: Deploy to OKE

Same steps as AKS deployment above.

---

## Part E: CI/CD with GitHub Actions

### Step 1: Configure Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

1. **KUBE_CONFIG**: Base64-encoded kubeconfig file
   ```bash
   # Get kubeconfig
   cat ~/.kube/config | base64 -w 0
   # Copy output and add as KUBE_CONFIG secret
   ```

2. **DOCKER_USERNAME**: Docker Hub username
3. **DOCKER_PASSWORD**: Docker Hub password or access token

### Step 2: Push to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit for Phase-V"

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/todo-app-phase-V.git

# Push to main
git branch -M main
git push -u origin main
```

### Step 3: Trigger CI/CD

The workflow will automatically run on every push to `main` branch.

**Workflow Steps:**
1. **Test:** Run pytest, linting, frontend build
2. **Build:** Build Docker images
3. **Push:** Push to GitHub Container Registry
4. **Deploy:** Deploy to Kubernetes cluster

### Step 4: Monitor Deployment

```bash
# Check workflow status
# GitHub → Actions tab

# Check deployment
kubectl get deployments -n todo-app
kubectl get pods -n todo-app
```

---

## Part F: Monitoring and Logging

### Dapr Dashboard

```bash
# Port forward to Dapr dashboard
kubectl port-forward svc/dapr-dashboard 8080:8080 -n dapr-system

# Visit http://localhost:8080
```

### Kubernetes Dashboard

```bash
# Enable dashboard addon
minikube addons enable dashboard

# Open dashboard
minikube dashboard
```

### View Logs

```bash
# Backend logs
kubectl logs -f deployment/todo-backend -n todo-app

# Frontend logs
kubectl logs -f deployment/todo-frontend -n todo-app

# Dapr sidecar logs
kubectl logs -f deployment/todo-backend -c daprd -n todo-app
```

### Check Events

```bash
# Kubernetes events
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

---

## Troubleshooting

### Issue: Pods not starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n todo-app

# Check logs
kubectl logs <pod-name> -n todo-app
```

### Issue: Dapr sidecar not injected

```bash
# Check Dapr annotations
kubectl get pod <pod-name> -n todo-app -o yaml | grep dapr

# Re-apply Dapr annotations
kubectl annotate pod <pod-name> dapr.io/enabled=true -n todo-app
```

### Issue: Kafka not connecting

```bash
# Check Kafka pods
kubectl get pods -n todo-app -l app.kubernetes.io/name=kafka

# Check Kafka logs
kubectl logs <kafka-pod> -n todo-app
```

### Issue: Reminders not sending

```bash
# Check Dapr Jobs component
kubectl get components.dapr.io dapr-jobs -n todo-app -o yaml

# Check job callback logs
kubectl logs deployment/todo-backend -n todo-app | grep "job trigger"
```

---

## Success Criteria Checklist

### Event-Driven Architecture
- [ ] Task creation publishes to Kafka
- [ ] Task update publishes to Kafka
- [ ] Task completion publishes to Kafka
- [ ] Task deletion publishes to Kafka
- [ ] Reminder creation publishes to Kafka
- [ ] Events consumed by appropriate services

### Dapr Integration
- [ ] Dapr Pub/Sub used for Kafka (not direct client)
- [ ] Dapr State used for conversation storage
- [ ] Dapr Jobs used for reminder scheduling
- [ ] Dapr Secrets used for credentials

### Recurring Tasks
- [ ] Task completion triggers recurring generation
- [ ] Next instance created automatically
- [ ] Kafka event published for generated instance

### Reminders
- [ ] Reminder scheduled via Dapr Jobs API
- [ ] Email sent at exact scheduled time
- [ ] No polling overhead

### Kubernetes
- [ ] All pods running with Dapr sidecars
- [ ] Services accessible
- [ ] Health checks passing

### CI/CD
- [ ] GitHub Actions workflow running
- [ ] Automated testing on push
- [ ] Automated deployment on main branch

---

## Next Steps

1. **Production Hardening:**
   - Increase Kafka replicas
   - Enable TLS for Kafka
   - Configure resource limits
   - Set up monitoring/alerting

2. **Scaling:**
   - Horizontal Pod Autoscaler (HPA)
   - Kafka partitioning for parallel processing
   - Database connection pooling

3. **Enhancements:**
   - Add distributed tracing (Jaeger/Zipkin)
   - Implement circuit breakers (Dapr)
   - Add rate limiting (Dapr)

---

## References

- **Dapr Documentation:** https://docs.dapr.io/
- **Strimzi (Kafka on K8s):** https://strimzi.io/
- **Minikube:** https://minikube.sigs.k8s.io/
- **Azure AKS:** https://docs.microsoft.com/en-us/azure/aks/
- **Oracle OKE:** https://docs.oracle.com/en-us/iaas/Content/ContEng/
- **GitHub Actions:** https://docs.github.com/en/actions

---

## Summary

Your Phase-V implementation includes:

✅ **Event-Driven Architecture** with Kafka and Dapr Pub/Sub
✅ **Recurring Tasks** triggered by task completion events
✅ **Reminders** scheduled with Dapr Jobs API (exact-time, no polling)
✅ **Full Dapr Integration** (Pub/Sub, State, Jobs, Secrets)
✅ **Kubernetes Deployment** (Minikube + Cloud: AKS/OKE)
✅ **CI/CD Pipeline** with GitHub Actions
✅ **Monitoring** via Dapr Dashboard and Kubernetes logs

**Everything is ready for deployment!** 🚀
