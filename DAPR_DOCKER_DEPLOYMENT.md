# 🐳 Dapr Notification Deployment Guide

## Overview

This guide explains the **Docker images and containers** required for your Todo App with Dapr-based notification system to work perfectly.

---

## 📦 Required Docker Images

### 1. **Your Application Images** (Build & Push Required)

| Image | Description | Dockerfile | Port |
|-------|-------------|------------|------|
| `naseerahmedwighio/todo-console-app-v-backend:latest` | FastAPI Backend | `backend/Dockerfile` | 7860 |
| `naseerahmedwighio/todo-console-app-v-frontend:latest` | Next.js Frontend | `frontend/Dockerfile` | 3000 |

**Build Commands:**
```powershell
# Windows PowerShell
.\build-docker-images.ps1

# Or manually:
cd backend
docker build -t naseerahmedwighio/todo-console-app-v-backend:latest .

cd ../frontend
docker build -t naseerahmedwighio/todo-console-app-v-frontend:latest .
```

**Push to Docker Hub:**
```powershell
docker push naseerahmedwighio/todo-console-app-v-backend:latest
docker push naseerahmedwighio/todo-console-app-v-frontend:latest
```

---

### 2. **Infrastructure Images** (Already Available)

These images are **already published** to your Docker Hub and used by `docker-compose.yml`:

| Image | Description | Port | Purpose |
|-------|-------------|------|---------|
| `confluentinc/cp-kafka:7.4.0` | Apache Kafka | 9092 | Event streaming for notifications |
| `confluentinc/cp-zookeeper:7.4.0` | Zookeeper | 2181 | Kafka coordination |
| `redis:7-alpine` | Redis Cache | 6379 | Celery broker & state store |

**Note:** These are official images - no need to build them!

---

### 3. **Dapr Runtime Images** (Already Available)

Dapr components use official Dapr images:

| Image | Description | Purpose |
|-------|-------------|---------|
| `daprio/daprd:1.12.0` | Dapr Sidecar | Runs alongside your backend |
| `daprio/dapr-placement:1.12.0` | Dapr Placement | Actor placement (optional) |
| `daprio/dapr-sentry:1.12.0` | Dapr Sentry | Certificate authority (optional) |
| `daprio/dapr-operator:1.12.0` | Dapr Operator | Kubernetes operator (K8s only) |

**Note:** These are official Dapr images - no need to build them!

---

## 🚀 Deployment Options

### Option 1: Docker Compose (Recommended for Local/Oracle VM)

Your current `docker-compose.yml` already includes all necessary services!

**Services in docker-compose.yml:**

```yaml
services:
  backend          # Your FastAPI backend
  frontend         # Your Next.js frontend
  zookeeper        # Kafka dependency
  kafka            # Event streaming
  redis            # Celery broker & Dapr state store
```

**To add Dapr sidecar to docker-compose:**

Create `docker-compose-dapr.yml`:

```yaml
version: '3.8'

services:
  backend:
    image: naseerahmedwighio/todo-console-app-v-backend:latest
    container_name: todo-backend
    ports:
      - "7860:7860"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - KAFKA_BOOTSTRAP_SERVERS=kafka:29092
      - CELERY_BROKER_URL=redis://redis:6379/0
      - JWT_SECRET=${JWT_SECRET}
      - SMTP_SERVER=${SMTP_SERVER}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - FROM_EMAIL=${FROM_EMAIL}
      - DAPR_HTTP_PORT=3500
      - DAPR_GRPC_PORT=50001
    depends_on:
      - redis
      - kafka
    networks:
      - todo-network

  # Dapr Sidecar for Backend
  dapr-sidecar:
    image: daprio/daprd:1.12.0
    container_name: todo-dapr-sidecar
    command: [
      "./daprd",
      "-app-id", "todo-backend",
      "-app-port", "7860",
      "-dapr-http-port", "3500",
      "-components-path", "/components"
    ]
    volumes:
      - ./dapr/components:/components
    depends_on:
      - backend
      - kafka
      - redis
    ports:
      - "3500:3500"
    networks:
      - todo-network

  frontend:
    image: naseerahmedwighio/todo-console-app-v-frontend:latest
    container_name: todo-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_BASE_URL=http://80.225.210.147:7860
    depends_on:
      - backend
    networks:
      - todo-network

  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    networks:
      - todo-network

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
    depends_on:
      - zookeeper
    networks:
      - todo-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - todo-network

networks:
  todo-network:
    driver: bridge
```

**Start all services:**
```bash
docker-compose -f docker-compose-dapr.yml up -d
```

---

### Option 2: Dapr CLI (Development)

Run backend with Dapr sidecar using `dapr run`:

```bash
# Start infrastructure first (Kafka, Redis)
docker-compose up -d kafka redis zookeeper

# Run backend with Dapr
cd backend
dapr run --app-id todo-backend \
  --app-port 7860 \
  --dapr-http-port 3500 \
  --components-path ../dapr/components \
  -- python -m uvicorn main:app --host 0.0.0.0 --port 7860

# Run frontend separately
cd ../frontend
npm run start
```

---

### Option 3: Kubernetes (Production)

For Kubernetes deployment with Dapr:

1. **Install Dapr on cluster:**
```bash
dapr init --kubernetes
```

2. **Apply Dapr components:**
```bash
kubectl apply -f dapr/components/
```

3. **Deploy backend with Dapr annotation:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "7860"
        dapr.io/enable-api-logging: "true"
    spec:
      containers:
      - name: backend
        image: naseerahmedwighio/todo-console-app-v-backend:latest
        ports:
        - containerPort: 7860
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "kafka:9092"
        - name: SMTP_SERVER
          valueFrom:
            secretKeyRef:
              name: smtp-secret
              key: server
```

---

## 🔧 Dapr Components Required

All components are in `dapr/components/`:

| Component | Type | Purpose |
|-----------|------|---------|
| `pubsub.yaml` | Kafka Pub/Sub | Event streaming |
| `scheduled-notifications.yaml` | Cron Binding | Triggers every minute for notifications |
| `recurring-tasks.yaml` | Cron Binding | Triggers every 5 minutes for recurring tasks |
| `notification-pubsub.yaml` | Kafka Pub/Sub | Notification events |
| `scheduled-notification-subscription.yaml` | Subscription | Routes events to handlers |
| `statestore.yaml` | PostgreSQL State | Persistent state storage |
| `secrets.yaml` | Secrets Store | Secure credential storage |

---

## ✅ Complete Container List

For your notification system to work perfectly, these containers must be running:

| Container | Image | Port | Required For |
|-----------|-------|------|--------------|
| `todo-backend` | `naseerahmedwighio/todo-console-app-v-backend` | 7860 | Main API |
| `todo-frontend` | `naseerahmedwighio/todo-console-app-v-frontend` | 3000 | Web UI |
| `todo-dapr-sidecar` | `daprio/daprd:1.12.0` | 3500 | Dapr runtime |
| `kafka` | `confluentinc/cp-kafka:7.4.0` | 9092 | Event streaming |
| `zookeeper` | `confluentinc/cp-zookeeper:7.4.0` | 2181 | Kafka coordination |
| `redis` | `redis:7-alpine` | 6379 | Celery broker, Dapr state |

**Total: 6 containers**

---

## 📝 Step-by-Step Deployment

### Step 1: Build Your Application Images

```powershell
# PowerShell
.\build-docker-images.ps1

# Tag for Docker Hub
docker tag todo-backend:latest naseerahmedwighio/todo-console-app-v-backend:latest
docker tag todo-frontend:latest naseerahmedwighio/todo-console-app-v-frontend:latest

# Push to Docker Hub
docker push naseerahmedwighio/todo-console-app-v-backend:latest
docker push naseerahmedwighio/todo-console-app-v-frontend:latest
```

### Step 2: Configure Environment

Create/update `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@ep-xxx-xxx-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# Email (Required for notifications!)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
FROM_EMAIL=your-email@gmail.com

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:29092

# Dapr
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
```

### Step 3: Start All Services

```bash
# Using docker-compose with Dapr
docker-compose -f docker-compose-dapr.yml up -d

# Verify all containers are running
docker ps

# Check logs
docker logs todo-backend
docker logs todo-dapr-sidecar
```

### Step 4: Verify Dapr Components

```bash
# List Dapr components
dapr components

# Check Dapr sidecar health
curl http://localhost:3500/v1.0/healthz

# Test scheduled notifications endpoint
curl http://localhost:3500/v1.0/bindings/scheduled-notifications
```

### Step 5: Test Notifications

```bash
# Send test email
curl -X POST "http://localhost:7860/api/v1/notifications/send-test-email" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Create recurring task
curl -X POST "http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=Test%20Bills&recurrence_pattern=pay_bills&by_monthday=1&notification_time=2026-03-21T09:00:00Z" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🔍 Monitoring & Debugging

### Check Container Status
```bash
docker ps -a
docker stats
```

### View Logs
```bash
# Backend logs
docker logs -f todo-backend

# Dapr sidecar logs
docker logs -f todo-dapr-sidecar

# Kafka logs
docker logs -f kafka

# All logs
docker-compose -f docker-compose-dapr.yml logs -f
```

### Test Dapr Cron Bindings
```bash
# Check if cron bindings are triggering
curl http://localhost:3500/v1.0/bindings/scheduled-notifications
curl http://localhost:3500/v1.0/bindings/recurring-tasks
```

### Check Database
```sql
-- View scheduled notifications
SELECT id, title, scheduled_time, notification_sent 
FROM todos 
WHERE scheduled_time <= NOW() 
AND notification_sent = FALSE;

-- View recurring tasks
SELECT * FROM recurring_tasks WHERE is_active = TRUE;
```

---

## ❗ Common Issues & Solutions

### Issue 1: Dapr Sidecar Not Connecting
**Solution:** Ensure backend starts before Dapr sidecar:
```yaml
depends_on:
  - backend
```

### Issue 2: Kafka Connection Refused
**Solution:** Use internal Docker network name:
```bash
KAFKA_BOOTSTRAP_SERVERS=kafka:29092  # Not localhost:9092
```

### Issue 3: Emails Not Sending
**Solution:** 
1. Verify SMTP credentials in `.env`
2. Check backend logs for email errors
3. Test with `/api/v1/notifications/send-test-email`

### Issue 4: Cron Bindings Not Triggering
**Solution:**
1. Verify Dapr components are loaded: `dapr components`
2. Check component YAML syntax
3. Restart Dapr sidecar

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │   Frontend   │───▶│    Backend   │◀────┐            │
│  │   (3000)     │    │    (7860)    │     │            │
│  └──────────────┘    └──────┬───────┘     │            │
│                             │             │            │
│                             ▼             │            │
│                       ┌─────────────┐     │            │
│                       │ Dapr Sidecar│─────┘            │
│                       │   (3500)    │                  │
│                       └──────┬──────┘                  │
│                              │                          │
│         ┌───────────────────┼───────────────────┐      │
│         ▼                   ▼                   ▼      │
│   ┌──────────┐       ┌──────────┐        ┌──────────┐ │
│   │  Kafka   │       │  Redis   │        │ Database │ │
│   │  (9092)  │       │  (6379)  │        │  (Neon)  │ │
│   └──────────┘       └──────────┘        └──────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   SMTP Server   │
                    │  (Gmail/Other)  │
                    └─────────────────┘
```

---

## 🎯 Summary

### Images You Need to Build & Push:
1. ✅ `naseerahmedwighio/todo-console-app-v-backend:latest`
2. ✅ `naseerahmedwighio/todo-console-app-v-frontend:latest`

### Images Already Available (No Build Needed):
1. ✅ `confluentinc/cp-kafka:7.4.0`
2. ✅ `confluentinc/cp-zookeeper:7.4.0`
3. ✅ `redis:7-alpine`
4. ✅ `daprio/daprd:1.12.0`

### Containers That Will Run:
1. ✅ `todo-backend`
2. ✅ `todo-frontend`
3. ✅ `todo-dapr-sidecar` (Dapr runtime)
4. ✅ `kafka`
5. ✅ `zookeeper`
6. ✅ `redis`

**Total: 6 containers for complete notification system!**

---

## 📚 Additional Resources

- [Dapr Documentation](https://docs.dapr.io/)
- [Dapr Cron Binding](https://docs.dapr.io/reference/components-reference/supported-bindings/cron/)
- [Kafka Docker Images](https://docs.confluent.io/platform/current/installation/docker/index.html)
- [Your Dapr Notification Guide](./DAPR_NOTIFICATION_GUIDE.md)
