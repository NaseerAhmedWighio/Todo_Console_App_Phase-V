# Phase-V: Advanced Cloud Deployment - Requirements Specification

## Overview
This specification defines the advanced features required for Phase-V of the Todo App, focusing on event-driven architecture with Kafka, Dapr integration, and Kubernetes deployment.

## Current State Analysis

### ✅ Already Implemented (Phase III & IV)
- Recurring Tasks with smart detection
- Email Reminders via Celery Beat
- Basic Kafka setup (Docker Compose)
- Basic Dapr Pub/Sub and State components
- SQLModel ORM with Neon PostgreSQL

### ❌ Gaps to Address for Phase-V

## Requirements

### REQ-001: Event-Driven Architecture with Kafka

**Description:** All task operations must publish events to Kafka topics for decoupled processing.

**Kafka Topics:**
| Topic | Producer | Consumer | Purpose |
|-------|----------|----------|---------|
| `task-events` | Chat API (MCP Tools) | Recurring Service, Audit Service | All task CRUD operations |
| `reminders` | Chat API (when due date set) | Notification Service | Scheduled reminder triggers |
| `task-updates` | Chat API | WebSocket Service | Real-time client sync |

**Event Schema - Task Event:**
```json
{
  "event_type": "created|updated|completed|deleted",
  "task_id": 123,
  "task_data": {},
  "user_id": "uuid",
  "timestamp": "2026-02-19T10:00:00Z"
}
```

**Event Schema - Reminder Event:**
```json
{
  "task_id": 123,
  "title": "Task Title",
  "due_at": "2026-03-15T18:00:00Z",
  "remind_at": "2026-03-14T18:00:00Z",
  "user_id": "uuid"
}
```

**Acceptance Criteria:**
- [ ] Every task create operation publishes to `task-events` topic
- [ ] Every task update operation publishes to `task-events` topic
- [ ] Every task complete operation publishes to `task-events` topic
- [ ] Every task delete operation publishes to `task-events` topic
- [ ] Reminder creation publishes to `reminders` topic
- [ ] Events contain all required fields per schema

---

### REQ-002: Recurring Task Event Consumer Service

**Description:** A dedicated service that consumes task events and auto-generates recurring task instances.

**Flow:**
```
Task Completed Event → Kafka "task-events" → Recurring Task Service → Creates next occurrence
```

**Acceptance Criteria:**
- [ ] Service consumes `task-events` topic
- [ ] Filters for `task.completed` events
- [ ] Checks if completed task is a recurring instance
- [ ] Generates next occurrence automatically
- [ ] Updates `last_generated_date` and `next_due_date`
- [ ] Publishes `recurring.instance_generated` event

---

### REQ-003: Notification Service with Dapr Jobs API

**Description:** Use Dapr Jobs API for exact-time reminder scheduling instead of Celery Beat polling.

**Why Jobs API over Cron Bindings:**
- Cron Bindings: Poll every X minutes, check DB (inefficient)
- Dapr Jobs API: Schedule exact time, callback fires (precise)

**Implementation:**
```python
# Schedule a reminder at exact time
async def schedule_reminder(task_id: int, remind_at: datetime, user_id: str):
    await httpx.post(
        f"http://localhost:3500/v1.0-alpha1/jobs/reminder-task-{task_id}",
        json={
            "dueTime": remind_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data": {
                "task_id": task_id,
                "user_id": user_id,
                "type": "reminder"
            }
        }
    )

# Handle callback when job fires
@app.post("/api/jobs/trigger")
async def handle_job_trigger(request: Request):
    job_data = await request.json()
    if job_data["data"]["type"] == "reminder":
        # Send email notification
        await send_email_notification(job_data["data"])
    return {"status": "SUCCESS"}
```

**Acceptance Criteria:**
- [ ] Dapr Jobs API configured
- [ ] Reminders scheduled at exact time via Jobs API
- [ ] Callback endpoint receives job triggers
- [ ] Email notifications sent on job trigger
- [ ] No polling overhead (event-driven)

---

### REQ-004: Dapr Full Integration

**Description:** Implement all Dapr building blocks for production-grade microservices.

**Components:**

| Component | Type | Purpose |
|-----------|------|---------|
| `kafka-pubsub` | pubsub.kafka | Event streaming (task-events, reminders) |
| `statestore` | state.postgresql | Conversation state, task cache |
| `dapr-jobs` | Jobs API | Trigger reminder checks |
| `kubernetes-secrets` | secretstores.kubernetes | API keys, DB credentials |

**Dapr Component Configurations:**

**1. Kafka Pub/Sub:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka:9092"
    - name: consumerGroup
      value: "todo-service"
```

**2. State Store:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        key: db-connection-string
    - name: tableName
      value: dapr_state
```

**3. Secrets Store:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
```

**Acceptance Criteria:**
- [ ] All 4 Dapr components configured
- [ ] Application uses Dapr Pub/Sub instead of direct Kafka
- [ ] Application uses Dapr State for conversation storage
- [ ] Application uses Dapr Jobs for reminders
- [ ] Secrets retrieved via Dapr Secrets API

---

### REQ-005: Minikube Local Deployment

**Description:** Deploy entire application stack to Minikube with Dapr sidecars.

**Pods:**
- Frontend Pod (Next.js + Dapr sidecar)
- Backend Pod (FastAPI + Dapr sidecar)
- Notification Service Pod (FastAPI + Dapr sidecar)
- Kafka Pod (or use Redpanda)
- Redis Pod (for Celery, optional if using Dapr Jobs)
- Dapr Sidecar (daprd)

**Deployment Steps:**
1. Install Minikube
2. Install Dapr on Kubernetes (`dapr init -k`)
3. Deploy Dapr components
4. Deploy application manifests
5. Verify all pods running

**Acceptance Criteria:**
- [ ] Kubernetes manifests created for all services
- [ ] Dapr components deployed to Minikube
- [ ] All pods running with Dapr sidecars
- [ ] Services accessible via kubectl port-forward
- [ ] Documentation for local deployment

---

### REQ-006: Cloud Deployment (Azure AKS / Google GKE / Oracle OKE)

**Description:** Deploy to production-grade Kubernetes cluster.

**Options:**
1. **Azure AKS** - $200 credit for 30 days
2. **Google GKE** - $300 credit for 90 days
3. **Oracle OKE** - Always free (4 OCPUs, 24GB RAM)

**Cloud Services:**
- **Kafka:** Redpanda Cloud (free serverless tier) or Confluent Cloud ($400 credit)
- **Database:** Neon PostgreSQL (existing)
- **Frontend:** Vercel or container in K8s
- **Backend:** Container in K8s

**Acceptance Criteria:**
- [ ] Cloud cluster created
- [ ] Dapr deployed to cloud cluster
- [ ] Application deployed with Helm charts
- [ ] Redpanda Cloud configured (or self-hosted Kafka)
- [ ] Public endpoint accessible
- [ ] Documentation for cloud deployment

---

### REQ-007: CI/CD Pipeline with GitHub Actions

**Description:** Automated build, test, and deployment pipeline.

**Workflow:**
```
Push to main → Run Tests → Build Docker Images → Push to Registry → Deploy to K8s
```

**Jobs:**
1. **Test:** Run pytest, linting, type checking
2. **Build:** Build Docker images for backend and frontend
3. **Push:** Push images to Docker Hub / GitHub Container Registry
4. **Deploy:** Update Kubernetes manifests, apply to cluster

**Acceptance Criteria:**
- [ ] `.github/workflows/ci.yml` created
- [ ] Tests run on every push
- [ ] Docker images built and pushed
- [ ] Deployment triggered on main branch
- [ ] Rollback capability

---

### REQ-008: Monitoring and Logging

**Description:** Configure observability for production deployment.

**Tools:**
- **Logging:** Loki + Promtail or ELK Stack
- **Metrics:** Prometheus + Grafana
- **Tracing:** Jaeger or Zipkin (via Dapr)

**Dapr Observability:**
- Built-in metrics (HTTP/gRPC calls, latency)
- Distributed tracing support
- Structured logging

**Acceptance Criteria:**
- [ ] Prometheus configured for metrics collection
- [ ] Grafana dashboards created
- [ ] Centralized logging configured
- [ ] Health checks on all services
- [ ] Alert rules for critical failures

---

## Implementation Priority

1. **Phase 1 (Event-Driven Core):**
   - REQ-001: Kafka event publishing
   - REQ-002: Recurring task consumer
   - REQ-003: Notification service with Dapr Jobs

2. **Phase 2 (Dapr Integration):**
   - REQ-004: Full Dapr components

3. **Phase 3 (Local Deployment):**
   - REQ-005: Minikube deployment

4. **Phase 4 (Cloud & CI/CD):**
   - REQ-006: Cloud deployment
   - REQ-007: CI/CD pipeline
   - REQ-008: Monitoring

---

## Success Criteria

### Recurring Tasks (Event-Driven)
- ✅ Task completion publishes to Kafka
- ✅ Recurring service consumes event
- ✅ Next occurrence created automatically
- ✅ No polling, fully event-driven

### Reminders (Dapr Jobs API)
- ✅ Reminder scheduled via Dapr Jobs API
- ✅ Exact-time trigger (no polling)
- ✅ Email sent at scheduled time
- ✅ Callback updates reminder status

### Dapr Integration
- ✅ All 4 building blocks in use
- ✅ No direct Kafka client code
- ✅ Secrets via Dapr API
- ✅ State management via Dapr

### Kubernetes
- ✅ Running on Minikube locally
- ✅ Running on cloud (AKS/GKE/OKE)
- ✅ Dapr sidecars on all pods
- ✅ Helm charts for deployment

### CI/CD
- ✅ GitHub Actions pipeline
- ✅ Automated testing
- ✅ Automated deployment

---

## Technical Debt to Address

1. **Celery Beat → Dapr Jobs:** Replace polling with exact-time scheduling
2. **Direct Kafka → Dapr Pub/Sub:** Abstract Kafka behind Dapr API
3. **Hardcoded Secrets → Dapr Secrets:** Use secret store
4. **Manual Deployment → CI/CD:** Automate everything

---

## Files to Create/Modify

### Backend
- `backend/app/events/publisher.py` - Add task event publishing
- `backend/app/events/consumer.py` - Add recurring task consumer
- `backend/app/services/notification_service.py` - Dapr Jobs integration
- `backend/app/api/jobs_routes.py` - Job callback endpoint
- `backend/app/dapr/jobs.py` - Dapr Jobs client
- `backend/app/dapr/secrets.py` - Dapr Secrets client

### Dapr Components
- `dapr/components/pubsub.yaml` - Update for Kafka
- `dapr/components/statestore.yaml` - Update for Neon
- `dapr/components/jobs.yaml` - Dapr Jobs component
- `dapr/components/secrets.yaml` - Kubernetes secrets

### Kubernetes
- `k8s/namespace.yaml` - Todo app namespace
- `k8s/backend-deployment.yaml` - Backend pod + Dapr sidecar
- `k8s/frontend-deployment.yaml` - Frontend pod + Dapr sidecar
- `k8s/notification-deployment.yaml` - Notification service
- `k8s/services.yaml` - Kubernetes services
- `k8s/ingress.yaml` - Ingress configuration

### CI/CD
- `.github/workflows/ci.yml` - CI/CD pipeline
- `.github/workflows/deploy.yml` - Deployment workflow

### Documentation
- `PHASE_V_DEPLOYMENT.md` - Complete deployment guide
- `KUBERNETES_SETUP.md` - K8s and Dapr setup
- `CLOUD_DEPLOYMENT.md` - Cloud provider setup

---

## Testing Checklist

### Recurring Tasks
- [ ] Create recurring task
- [ ] Complete task instance
- [ ] Verify next instance created via Kafka event
- [ ] Check event published to `task-events`

### Reminders
- [ ] Create task with reminder
- [ ] Verify Dapr Job scheduled
- [ ] Wait for scheduled time
- [ ] Verify email received
- [ ] Check reminder status updated

### Dapr
- [ ] Publish event via Dapr Pub/Sub
- [ ] Retrieve state via Dapr State
- [ ] Schedule job via Dapr Jobs API
- [ ] Get secret via Dapr Secrets

### Kubernetes
- [ ] All pods running
- [ ] Dapr sidecars injected
- [ ] Services accessible
- [ ] Health checks passing

---

## References

- **Phase-V Requirements:** Hackathon Phase-V specification document
- **Dapr Documentation:** https://docs.dapr.io/
- **Kafka Documentation:** https://kafka.apache.org/documentation/
- **Minikube:** https://minikube.sigs.k8s.io/docs/
- **Redpanda Cloud:** https://redpanda.com/cloud
