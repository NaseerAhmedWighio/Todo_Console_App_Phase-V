# Quick Start Guide: Advanced Todo Features - Phase III

**Feature**: 003-advanced-todo-features  
**Date**: 2026-02-19  
**Version**: 1.0.0

---

## Overview

This guide walks you through setting up and testing the advanced todo features including recurring tasks, reminders, priorities, tags, search, filtering, sorting, event-driven architecture, and Dapr distributed runtime.

**Prerequisites**:
- Phase II (002-todo-fullstack) fully deployed and working
- Docker & Docker Compose installed
- Node.js 18+ and Python 3.11+ installed
- Existing Neon PostgreSQL database configured

---

## Step 1: Infrastructure Setup

### 1.1 Install New Dependencies

**Backend**:
```bash
cd backend
pip install -r requirements.txt
```

**New Dependencies Added**:
```txt
kafka-python>=2.0.2
dapr-sdk>=1.10.0
celery>=5.3.0
redis>=4.5.0
python-dateutil>=2.8.2
pytz>=2023.3
```

**Frontend**:
```bash
cd frontend
npm install
```

**New Dependencies Added**:
```json
{
  "date-fns": "^2.30.0",
  "react-tag-autocomplete": "^7.0.0",
  "@dnd-kit/core": "^6.0.0"
}
```

---

### 1.2 Start Kafka and Redis

```bash
# From project root
docker-compose up -d kafka redis
```

**Verify Services**:
```bash
docker-compose ps
# Should show:
# - kafka: Running
# - redis: Running
```

**Kafka Configuration** (docker-compose.yml):
```yaml
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
  depends_on:
    - zookeeper

zookeeper:
  image: confluentinc/cp-zookeeper:7.4.0
  ports:
    - "2181:2181"
  environment:
    ZOOKEEPER_CLIENT_PORT: 2181
```

---

### 1.3 Initialize Dapr

**Install Dapr CLI** (if not already installed):
```bash
# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Windows (PowerShell)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash"
```

**Initialize Dapr**:
```bash
dapr init
```

**Verify Dapr**:
```bash
dapr --version
# Should show:
# CLI version: 1.10.0
# Runtime version: 1.10.0
```

---

### 1.4 Configure Dapr Components

**Create Dapr State Store** (`dapr/components/statestore.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "postgresql://neondb_owner:password@ep-sweet-feather-ahvkyo80-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
  - name: tableName
    value: dapr_state
```

**Create Dapr Pub/Sub** (`dapr/components/pubsub.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "localhost:9092"
  - name: consumerGroup
    value: "todo-app"
  - name: publishTopic
    value: "todo-events"
  - name: authType
    value: "none"
```

**Copy Components to Dapr Directory**:
```bash
# macOS/Linux
cp -r dapr/components ~/.dapr/components/

# Windows (PowerShell)
Copy-Item -Path dapr/components -Destination $env:USERPROFILE\.dapr\components -Recurse
```

---

## Step 2: Database Migrations

### 2.1 Run Schema Migrations

```bash
cd backend

# Create migration (if using alembic)
alembic revision --autogenerate -m "Add advanced todo features"

# Apply migration
alembic upgrade head
```

**Alternative (Manual SQL)**:
```bash
# Run the SQL schema from data-model.md
psql $DATABASE_URL -f specs/003-advanced-todo-features/data-model-migration.sql
```

### 2.2 Verify Migration

```bash
# Connect to database
psql $DATABASE_URL

# Check new tables exist
\dt

# Should show:
# - tags
# - task_tags
# - reminders
# - recurring_tasks
# - domain_events
# - dapr_state
```

---

## Step 3: Backend Setup

### 3.1 Update Environment Variables

**backend/.env** (add these):
```bash
# Existing variables...

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_PREFIX=todo

# Dapr Configuration
DAPR_HTTP_ENDPOINT=http://127.0.0.1:3500
DAPR_GRPC_ENDPOINT=http://127.0.0.1:50001
DAPR_STATESTORE_NAME=todo-statestore
DAPR_PUBSUB_NAME=todo-pubsub

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Reminder Configuration
REMINDER_CHECK_INTERVAL_MINUTES=1
MAX_REMINDER_RETRIES=3
```

### 3.2 Start Backend with Dapr

**Option A: Development Mode**:
```bash
cd backend

# Start with Dapr sidecar
dapr run \
  --app-id todo-backend \
  --app-port 7860 \
  --dapr-http-port 3500 \
  --dapr-grpc-port 50001 \
  --resources-path ../dapr/components \
  -- uvicorn main:app --reload --host 0.0.0.0 --port 7860
```

**Option B: Docker Compose** (Recommended for production):
```bash
# From project root
docker-compose up -d backend dapr-sidecar
```

### 3.3 Start Celery Workers

```bash
cd backend

# Start Celery worker for background tasks
celery -A app.workers.celery_app worker --loglevel=info --detach

# Start Celery beat for scheduled tasks
celery -A app.workers.celery_app beat --loglevel=info --detach
```

**Verify Workers**:
```bash
celery -A app.workers.celery_app inspect ping
# Should respond with: OK
```

---

## Step 4: Frontend Setup

### 4.1 Update Environment Variables

**frontend/.env.local** (add these):
```bash
# Existing variables...

# Feature Flags
NEXT_PUBLIC_ADVANCED_FEATURES_ENABLED=true
NEXT_PUBLIC_SEARCH_ENABLED=true
NEXT_PUBLIC_REMINDERS_ENABLED=true
NEXT_PUBLIC_RECURRING_TASKS_ENABLED=true
```

### 4.2 Start Frontend

```bash
cd frontend
npm run dev
```

**Verify Frontend**:
- Open http://localhost:3000
- Login with your credentials
- Navigate to dashboard

---

## Step 5: Verification Tests

### 5.1 Test Priority Feature

**Via UI**:
1. Create a new task
2. Select priority: "High" from dropdown
3. Save task
4. Verify task shows with red priority indicator

**Via API**:
```bash
curl -X POST http://localhost:7860/api/v1/todos \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "High priority task",
    "priority": "high",
    "description": "Test priority feature"
  }'

# Response should include: "priority": "high"
```

---

### 5.2 Test Tags Feature

**Via UI**:
1. Create a new tag: "Work" with blue color
2. Create another tag: "Personal" with green color
3. Edit a task and assign both tags
4. Filter tasks by "Work" tag
5. Verify only "Work" tasks are shown

**Via API**:
```bash
# Create tag
curl -X POST http://localhost:7860/api/v1/tags \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "work",
    "color": "#3B82F6"
  }'

# Assign tag to task
curl -X POST http://localhost:7860/api/v1/tags/TAG_ID/assign \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task_id": "TASK_ID"}'

# Filter by tag
curl "http://localhost:7860/api/v1/todos?tag_id=TAG_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 5.3 Test Search Feature

**Via UI**:
1. Create multiple tasks with different titles
2. Use search bar to search for a keyword
3. Verify matching tasks appear instantly
4. Try search with filters (priority, status)

**Via API**:
```bash
# Search tasks
curl "http://localhost:7860/api/v1/search?q=groceries&priority=high" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response should include matching tasks with relevance scores
```

---

### 5.4 Test Recurring Tasks

**Via UI**:
1. Create a new task
2. Enable "Recurring" toggle
3. Select pattern: "Weekly"
4. Select weekdays: Monday, Wednesday, Friday
5. Save task
6. Verify next occurrence is shown

**Via API**:
```bash
# Configure recurring task
curl -X POST http://localhost:7860/api/v1/todos/TASK_ID/recurring \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recurrence_pattern": "weekly",
    "interval": 1,
    "by_weekday": "0,2,4",
    "end_condition": "never"
  }'

# Verify recurring configuration
curl http://localhost:7860/api/v1/todos/TASK_ID/recurring \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Test Instance Generation**:
```bash
# Wait for background worker to generate next instance
# Check recurring_tasks table:
psql $DATABASE_URL -c "SELECT next_due_date FROM recurring_tasks WHERE task_id = 'TASK_ID';"

# Verify new task instance was created:
psql $DATABASE_URL -c "SELECT * FROM tasks WHERE recurring_task_id = 'RECURRING_ID' ORDER BY created_at DESC LIMIT 1;"
```

---

### 5.5 Test Reminders

**Via UI**:
1. Edit a task with a due date
2. Click "Add Reminder"
3. Set reminder: "1 day before" via "Email"
4. Save task
5. Verify reminder appears in reminders list

**Via API**:
```bash
# Create reminder
curl -X POST http://localhost:7860/api/v1/reminders \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "TASK_ID",
    "timing_minutes": 1440,
    "delivery_channel": "email"
  }'

# Verify reminder
curl http://localhost:7860/api/v1/reminders \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Test Reminder Delivery**:
```bash
# Create a task with due date in 2 minutes
# Create a reminder for 1 minute before
# Wait for reminder time
# Check reminders table:
psql $DATABASE_URL -c "SELECT status, sent_at FROM reminders WHERE task_id = 'TASK_ID';"

# Should show: status = 'sent', sent_at = [timestamp]

# Check email logs (if using SendGrid):
# Check backend logs for reminder delivery confirmation
```

---

### 5.6 Test Event-Driven Architecture

**Verify Event Publishing**:
```bash
# Create a task
curl -X POST http://localhost:7860/api/v1/todos \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test event", "priority": "high"}'

# Check domain_events table:
psql $DATABASE_URL -c "SELECT event_type, payload, published FROM domain_events ORDER BY created_at DESC LIMIT 5;"

# Should show:
# - event_type: 'task.created'
# - payload: {"title": "Test event", ...}
# - published: false (until Kafka publisher runs)
```

**Verify Kafka Events**:
```bash
# Consume events from Kafka topic
docker-compose exec kafka \
  kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic todo.tasks.created --from-beginning

# Create another task
# Should see event appear in consumer output
```

---

### 5.7 Test Dapr State Management

**Test State Save**:
```bash
# Save state via Dapr API
curl -X POST http://localhost:3500/v1.0/state/todo-statestore \
  -H "Content-Type: application/json" \
  -d '[
    {
      "key": "user:USER_ID:settings",
      "value": {"theme": "dark", "timezone": "America/New_York"}
    }
  ]'

# Retrieve state
curl http://localhost:3500/v1.0/state/todo-statestore/user:USER_ID:settings

# Should return: {"theme": "dark", "timezone": "America/New_York"}
```

**Verify Database**:
```bash
psql $DATABASE_URL -c "SELECT key, value FROM dapr_state WHERE key = 'user:USER_ID:settings';"
```

---

### 5.8 Test Filter & Sort

**Via UI**:
1. Create multiple tasks with different priorities and due dates
2. Apply filter: Priority = "High"
3. Apply sort: Due Date (Ascending)
4. Verify high-priority tasks shown, sorted by due date

**Via API**:
```bash
# Filter and sort
curl "http://localhost:7860/api/v1/todos?priority=high&sort_by=due_date&sort_order=asc" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Multiple filters
curl "http://localhost:7860/api/v1/todos?priority=high&status=pending&tag_id=TAG_ID&sort_by=priority" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Step 6: Troubleshooting

### Common Issues

**Issue: Kafka Connection Failed**
```
Error: KafkaConnectionError: Unable to connect to Kafka broker
```

**Solution**:
```bash
# Check Kafka is running
docker-compose ps kafka

# Check Kafka logs
docker-compose logs kafka

# Verify connection string
echo $KAFKA_BOOTSTRAP_SERVERS
# Should be: localhost:9092

# Test Kafka connection
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```

---

**Issue: Dapr Sidecar Not Starting**
```
Error: connection error: desc = "transport: Error while dialing dial tcp 127.0.0.1:50001: connect: connection refused"
```

**Solution**:
```bash
# Check Dapr is initialized
dapr --version

# Check components directory
ls ~/.dapr/components/

# Restart Dapr
dapr stop --app-id todo-backend
dapr run --app-id todo-backend --app-port 7860 -- uvicorn main:app --reload
```

---

**Issue: Celery Workers Not Processing Tasks**
```
Task reminder_service.send_reminder not found
```

**Solution**:
```bash
# Restart Celery workers
celery -A app.workers.celery_app worker --loglevel=info --detach

# Check worker logs
tail -f celery-worker.log

# Verify task registration
celery -A app.workers.celery_app inspect registered
```

---

**Issue: Search Not Returning Results**
```
Search returns 0 results for known tasks
```

**Solution**:
```bash
# Check search_vector is populated
psql $DATABASE_URL -c "SELECT id, title, search_vector FROM tasks LIMIT 5;"

# Rebuild search index
psql $DATABASE_URL -c "REFRESH MATERIALIZED VIEW CONCURRENTLY IF EXISTS tasks_search_view;"

# Or reindex
psql $DATABASE_URL -c "REINDEX INDEX idx_tasks_search_vector;"
```

---

**Issue: Reminders Not Being Sent**
```
Reminders stay in 'pending' status
```

**Solution**:
```bash
# Check Celery beat is running
ps aux | grep celery

# Check reminder worker logs
tail -f logs/reminder_worker.log

# Manually trigger reminder processing
python -c "from app.services.reminder_service import ReminderService; import asyncio; asyncio.run(ReminderService().process_due_reminders())"

# Check database for pending reminders
psql $DATABASE_URL -c "SELECT COUNT(*) FROM reminders WHERE status = 'pending' AND scheduled_time <= NOW();"
```

---

## Step 7: Performance Benchmarks

### Expected Performance

| Operation | Target | How to Measure |
|-----------|--------|----------------|
| Search (10k tasks) | < 3 seconds | Use browser DevTools Network tab |
| Filter + Sort (1k tasks) | < 1 second | API response time |
| Event Publishing | < 100ms (p95) | Check domain_events.published_at - created_at |
| Reminder Delivery | < 1 minute delay | Check reminders.sent_at - scheduled_time |
| Recurring Instance Generation | < 1 second per instance | Check recurring_tasks.last_generated_date |

### Benchmark Commands

```bash
# Search performance
time curl "http://localhost:7860/api/v1/search?q=test" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter + Sort performance
time curl "http://localhost:7860/api/v1/todos?priority=high&sort_by=due_date" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Event publishing latency
psql $DATABASE_URL -c "SELECT AVG(EXTRACT(EPOCH FROM (published_at - created_at))) as avg_latency FROM domain_events WHERE published = true;"
```

---

## Next Steps

After successful verification:

1. **Deploy to Production**:
   - Update docker-compose.yml for production
   - Configure Kafka cluster for production
   - Set up Dapr in production environment
   - Configure monitoring and alerting

2. **Monitor Performance**:
   - Set up Kafka monitoring (lag, throughput)
   - Monitor Dapr metrics (state operations, pub/sub)
   - Track Celery task success rates
   - Monitor database query performance

3. **User Onboarding**:
   - Update user documentation
   - Create tutorial videos for new features
   - Send announcement email to users
   - Monitor user adoption metrics

---

## Support

**Documentation**:
- [Spec](spec.md) - Feature specification
- [Plan](plan.md) - Implementation plan
- [Data Model](data-model.md) - Database schema
- [API Contracts](contracts/api-contracts.md) - API documentation

**Logs**:
- Backend: `backend/logs/`
- Frontend: `frontend/logs/`
- Celery: `backend/celery-worker.log`
- Dapr: `~/.dapr/logs/`

**Contact**:
- Development Team: dev@example.com
- Support: support@example.com
