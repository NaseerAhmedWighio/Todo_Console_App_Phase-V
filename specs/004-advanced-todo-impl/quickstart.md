# Quick Start Guide: Advanced Todo Features Implementation

**Feature**: 004-advanced-todo-impl
**Date**: 2026-02-20
**Prerequisites**: Phase II setup complete

---

## Overview

This guide walks you through setting up and verifying all advanced todo features including priorities, tags, due dates, search, filter, sort, recurring tasks, reminders, event-driven architecture with Kafka, and distributed runtime with Dapr.

---

## Prerequisites

Before starting, ensure you have:

- ✅ Docker & Docker Compose installed
- ✅ Node.js 18+ and npm installed
- ✅ Python 3.11 installed
- ✅ Phase II features working (authentication, basic CRUD)
- ✅ NeonDB PostgreSQL connection configured
- ✅ OpenRouter API key configured

---

## Step 1: Install New Dependencies

### Backend Dependencies

```bash
cd backend

# Add new dependencies to requirements.txt
echo "kafka-python>=2.0.2" >> requirements.txt
echo "dapr-sdk>=1.10.0" >> requirements.txt
echo "dapr-ext-fastapi>=1.10.0" >> requirements.txt
echo "celery>=5.3.0" >> requirements.txt
echo "redis>=4.5.0" >> requirements.txt
echo "python-dateutil>=2.8.2" >> requirements.txt
echo "pytz>=2023.3" >> requirements.txt

# Install dependencies
pip install -r requirements.txt
```

### Frontend Dependencies

```bash
cd frontend

# Add new dependencies
npm install date-fns @dnd-kit/core react-tag-autocomplete

# Or using the package manager of your choice
```

---

## Step 2: Database Migrations

Run the database migrations to add new tables and columns:

```bash
cd backend

# Run migrations (using your migration tool of choice)
python -m sqlmodel_migrate upgrade
```

### Migrations Applied

The migration script will:

1. **Create new tables**:
   - `tags` - User-defined labels
   - `task_tags` - Many-to-many join table
   - `reminders` - Scheduled notifications
   - `recurring_tasks` - Recurrence patterns
   - `domain_events` - Event tracking

2. **Extend existing tables**:
   - `tasks` - Add priority, due_date, timezone, is_recurring, recurring_task_id
   - `users` - Add timezone, notification_preferences, default_task_priority

3. **Create indexes**:
   - All performance-critical indexes from data-model.md
   - GIN index for full-text search

---

## Step 3: Start Infrastructure Services

### Start Kafka, Redis, and Dapr

```bash
# From project root
docker-compose up -d kafka zookeeper redis dapr
```

### Verify Services

```bash
# Check container status
docker-compose ps

# Expected output:
# NAME                STATUS
# kafka               Up
# zookeeper           Up
# redis               Up
# dapr                Up
```

### Initialize Dapr

```bash
# Initialize Dapr locally
dapr init

# Verify Dapr is running
dapr status
```

---

## Step 4: Configure Dapr Components

Create Dapr component configuration files:

### State Store Configuration

```yaml
# dapr/components/statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "postgresql://user:password@neon-host:5432/dbname?sslmode=require"
```

### Pub/Sub Configuration

```yaml
# dapr/components/pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "localhost:9092"
```

---

## Step 5: Start Backend with Dapr

```bash
cd backend

# Start backend with Dapr sidecar
dapr run \
  --app-id todo-backend \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --components-path ../dapr/components \
  -- python main.py
```

### Verify Backend

```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Check Dapr connectivity
curl http://localhost:8000/api/v1/health/dapr
```

---

## Step 6: Start Frontend

```bash
cd frontend

# Start development server
npm run dev
```

Open http://localhost:3000 in your browser.

---

## Step 7: Start Background Workers

### Start Celery Worker

```bash
cd backend

# Start Celery worker for reminders and recurring tasks
celery -A app.workers.celery_app worker --loglevel=info &

# Start Celery beat for scheduled tasks
celery -A app.workers.celery_app beat --loglevel=info &
```

---

## Verification Checklist

### ✅ Priorities

1. Create a task with "urgent" priority
2. Create another task with "low" priority
3. Sort by priority → urgent task should appear first
4. Filter by "high" priority → only high priority tasks shown

**Expected**: Tasks display with color-coded priority indicators

---

### ✅ Tags

1. Create a tag named "Work" with blue color
2. Create a tag named "Personal" with green color
3. Assign tags to different tasks
4. Filter by "Work" tag → only work tasks shown

**Expected**: Tags displayed as colored badges on tasks

---

### ✅ Due Dates

1. Create a task with due date in the past (yesterday)
2. Create a task with due date tomorrow
3. View task list

**Expected**: Overdue task displayed with red styling

---

### ✅ Search

1. Create several tasks with different titles
2. Search for a keyword in the search box
3. Verify results match search query

**Expected**: Results appear within 3 seconds with relevance ranking

---

### ✅ Filter & Sort

1. Apply multiple filters (status=active, priority=high)
2. Apply sorting (sort by due_date)
3. Verify results match combined criteria

**Expected**: Filtered and sorted results displayed correctly

---

### ✅ Recurring Tasks

1. Create a task
2. Configure it as recurring (daily pattern)
3. Wait for background worker to run (or trigger manually)
4. Check for new instance generation

**Expected**: New task instance created automatically

---

### ✅ Reminders

1. Create a task with a due date
2. Add a reminder (15 minutes before)
3. Wait for reminder time (or simulate)
4. Check reminder status

**Expected**: Reminder status changes to "sent"

---

### ✅ Event-Driven Architecture

1. Create a task
2. Check domain events table
3. Verify event published to Kafka

**Expected**: `task.created` event visible in events table

---

### ✅ Dapr Integration

1. Check Dapr sidecar connectivity
2. Verify state management working
3. Check pub/sub communication

**Expected**: All Dapr health checks pass

---

## Troubleshooting

### Kafka Connection Issues

```bash
# Check Kafka logs
docker-compose logs kafka

# Restart Kafka
docker-compose restart kafka
```

### Dapr Sidecar Not Connecting

```bash
# Check Dapr logs
dapr logs --app-id todo-backend

# Restart Dapr
dapr stop --app-id todo-backend
dapr run --app-id todo-backend --app-port 8000 -- python main.py
```

### Celery Worker Not Processing

```bash
# Check Celery worker logs
celery -A app.workers.celery_app worker --loglevel=debug

# Verify Redis is running
docker-compose ps redis
```

### Database Migration Errors

```bash
# Check current migration status
python -m sqlmodel_migrate current

# Rollback if needed
python -m sqlmodel_migrate downgrade -1

# Re-run migrations
python -m sqlmodel_migrate upgrade
```

---

## Next Steps

1. **Run Tests**: Execute test suite to verify all features
   ```bash
   cd backend && pytest
   cd frontend && npm test
   ```

2. **Deploy**: Follow deployment guide for production setup

3. **Monitor**: Set up monitoring and alerting for Kafka, Dapr, and Celery

---

## References

- Full specification: [spec.md](spec.md)
- Implementation plan: [plan.md](plan.md)
- Data model: [data-model.md](data-model.md)
- API contracts: [contracts/api-contracts.yaml](contracts/api-contracts.yaml)
- Research findings: [research.md](research.md)
