# Project Architecture Analysis
## Todo App Phase V - Complete System Overview

**Date:** March 10, 2026  
**Tech Stack:** FastAPI (Backend), Next.js (Frontend), Neon PostgreSQL, Kafka, Dapr, Celery

---

## 📊 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            FRONTEND (Next.js)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐│
│  │  Login   │  │ Register │  │Dashboard │  │  WebSocket Connection    ││
│  │  Page    │  │  Page    │  │  Page    │  │  (Real-time Updates)     ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST API
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI)                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      API Routes Layer                             │  │
│  │  /auth  /todos  /recurring  /reminders  /chat  /tags  /search    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│                                    ▼                                    │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                     Services Layer                                │  │
│  │  TaskService  EventService  EmailService  SearchService  ...     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│         ┌──────────────────────────┼──────────────────────────┐         │
│         │                          │                          │         │
│         ▼                          ▼                          ▼         │
│  ┌─────────────┐           ┌─────────────┐            ┌─────────────┐  │
│  │   Kafka     │           │    Dapr     │            │   Celery    │  │
│  │  (Events)   │           │  (Pub/Sub)  │            │  (Workers)  │  │
│  └─────────────┘           └─────────────┘            └─────────────┘  │
│         │                          │                          │         │
│         │                          │                          │         │
│         ▼                          ▼                          ▼         │
│  ┌─────────────┐           ┌─────────────┐            ┌─────────────┐  │
│  │  Event      │           │  State      │            │  Reminder   │  │
│  │  Consumer   │           │  Store      │            │  Worker     │  │
│  │  Worker     │           │             │            │  Recurring  │  │
│  └─────────────┘           └─────────────┘            │  Worker     │  │
│                                                     │  Event      │  │
│                                                     │  Worker     │  │
│                                                     └─────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      DATABASE (Neon PostgreSQL)                         │
│  Tables: users, todos, recurring_tasks, reminders, domain_events,      │
│          tags, task_tags, conversations, messages, email_verifications  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 RECURRING TASK SYSTEM

### How It Works

```
User Creates Recurring Task
         │
         ▼
┌─────────────────────────┐
│  POST /api/v1/todos/    │  ← Create base task
└─────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  POST /api/v1/recurring/tasks/  │  ← Configure recurrence
│  {                              │
│    "recurrence_pattern": "daily",│
│    "interval": 1,               │
│    "by_weekday": "MO,WE,FR",    │
│    "end_condition": "never"     │
│  }                              │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Database State:                        │
│  - Todo.is_recurring = true             │
│  - RecurringTask created                │
│  - next_due_date calculated             │
└─────────────────────────────────────────┘
         │
         └───────────────────────────────────────┐
                                                 │
                    ┌────────────────────────────┘
                    │
         ┌──────────▼──────────┐
         │  Celery Beat        │
         │  (Every Hour)       │
         │  Cron: 0 * * * *    │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────────┐
         │  generate_recurring_    │
         │  instances() task       │
         └──────────┬──────────────┘
                    │
                    ▼
         ┌─────────────────────────────────────┐
         │  For each active recurring task:    │
         │  1. Check if next_due_date <= now   │
         │  2. Check end conditions            │
         │  3. Create new Todo instance        │
         │  4. Update next_due_date            │
         │  5. Publish event to Kafka          │
         └──────────┬──────────────────────────┘
                    │
                    ▼
         ┌─────────────────────────────────────┐
         │  New Task Instance Created:         │
         │  - Cloned from base task            │
         │  - New due_date calculated          │
         │  - recurring_task_id linked         │
         │  - is_recurring = false (instance)  │
         └─────────────────────────────────────┘
```

### Recurrence Patterns Supported

| Pattern | Description | Configuration |
|---------|-------------|---------------|
| **Daily** | Every N days | `recurrence_pattern: "daily"`, `interval: 1` |
| **Weekly** | Every N weeks on specific weekdays | `recurrence_pattern: "weekly"`, `by_weekday: "MO,WE,FR"` |
| **Monthly** | Every N months on specific day | `recurrence_pattern: "monthly"`, `by_monthday: 15` |
| **Yearly** | Every N years on specific month | `recurrence_pattern: "yearly"`, `by_month: "1,6,12"` |

### End Conditions

1. **Never** (`end_condition: "never"`) - Continues indefinitely
2. **After Occurrences** (`end_condition: "after_occurrences"`, `end_occurrences: 10`) - Stops after N instances
3. **On Date** (`end_condition: "on_date"`, `end_date: "2026-12-31"`) - Stops on specific date

### Key Files

- **`backend/app/workers/recurring_worker.py`** - Celery task for generating instances
- **`backend/app/api/recurring_routes.py`** - API endpoints for recurring configuration
- **`backend/app/models/recurring_task.py`** - RecurringTask model
- **`backend/app/workers/celery_app.py`** - Celery Beat schedule (runs every hour)

---

## ⏰ REMINDER SYSTEM

### How It Works

```
User Creates Task with Due Date
         │
         ▼
┌─────────────────────────────────┐
│  POST /api/v1/reminders/        │
│  {                              │
│    "task_id": "uuid",           │
│    "timing_minutes": 30,        │  ← Remind 30 minutes before
│    "timing_days": 1,            │  ← OR 1 day before
│    "delivery_channel": "email"  │
│  }                              │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Reminder Record Created:               │
│  - scheduled_time = due_date - offset   │
│  - status = "pending"                   │
│  - delivery_channel = "email"           │
└─────────────────────────────────────────┘
         │
         └───────────────────────────────────────┐
                                                 │
                    ┌────────────────────────────┘
                    │
         ┌──────────▼──────────┐
         │  Celery Beat        │
         │  (Every Minute)     │
         │  Cron: */1 * * * *  │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────────┐
         │  process_due_reminders()│
         │  (Celery Task)          │
         └──────────┬──────────────┘
                    │
                    ▼
         ┌─────────────────────────────────────┐
         │  Query:                             │
         │  SELECT reminders WHERE             │
         │    scheduled_time <= now AND        │
         │    status = "pending"               │
         └──────────┬──────────────────────────┘
                    │
                    ▼
         ┌─────────────────────────────────────┐
         │  For each due reminder:             │
         │  1. Check user email verified       │
         │  2. Check not sent recently         │
         │  3. Send email via SMTP             │
         │  4. Update status = "sent"          │
         │  5. Publish event to Kafka          │
         └──────────┬──────────────────────────┘
                    │
                    ▼
         ┌─────────────────────────────────────┐
         │  Email Sent to User:                │
         │  "Task 'Buy groceries' is due       │
         │   at 3:00 PM UTC"                   │
         └─────────────────────────────────────┘
```

### Reminder Delivery Channels

| Channel | Description | Status |
|---------|-------------|--------|
| **in_app** | In-app notification via WebSocket | ✅ Implemented |
| **email** | Email reminder via SMTP | ✅ Implemented |
| **web_push** | Browser push notifications | 🔧 Available (not configured) |
| **sms** | SMS notifications | 🔧 Available (not configured) |

### Reminder Timing Options

- **Minutes before**: `timing_minutes: 30` → Remind 30 minutes before due date
- **Days before**: `timing_days: 1` → Remind 1 day before due date
- **Combined**: Both can be set, days takes precedence

### Key Files

- **`backend/app/workers/reminder_worker.py`** - Worker that sends reminders
- **`backend/app/api/reminder_routes.py`** - API endpoints for reminders
- **`backend/app/models/reminder.py`** - Reminder model
- **`backend/app/services/email_service.py`** - Email sending service
- **`backend/app/workers/celery_app.py`** - Celery Beat schedule (runs every minute)

---

## 📡 KAFKA - Event Streaming

### Where Kafka Is Used

```
┌──────────────────────────────────────────────────────────────────────┐
│                         KAFKA TOPICS                                  │
├──────────────────────────────────────────────────────────────────────┤
│  Topic Name              │ Event Types               │ Consumers     │
├──────────────────────────────────────────────────────────────────────┤
│  todo.tasks.created      │ task.created              │ - Analytics   │
│  todo.tasks.updated      │ task.updated              │ - Search      │
│  todo.tasks.completed    │ task.completed            │ - Recurring   │
│  todo.tasks.deleted      │ task.deleted              │ - Audit Log   │
├──────────────────────────────────────────────────────────────────────┤
│  todo.reminders          │ task.reminder_sent        │ - Logging     │
├──────────────────────────────────────────────────────────────────────┤
│  todo.recurring          │ recurring.instance_generated│ - Dashboard │
├──────────────────────────────────────────────────────────────────────┤
│  todo-events             │ ALL_EVENTS (catch-all)    │ - Backup      │
└──────────────────────────────────────────────────────────────────────┘
```

### Event Flow

```
┌─────────────┐
│  API Route  │  (e.g., create_todo)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Service    │  (e.g., TaskService)
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  EventService.publish_and_track()       │
│  1. Create DomainEvent in DB            │
│  2. Publish to Kafka                    │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Kafka Producer                         │
│  Topic: todo.tasks.created              │
│  Message: {                             │
│    "event_type": "task.created",        │
│    "payload": {...},                    │
│    "user_id": "uuid",                   │
│    "timestamp": "2026-03-10T..."        │
│  }                                      │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Kafka Broker                           │
│  - Stores message                       │
│  - Replicates to followers              │
│  - Manages consumer offsets             │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Kafka Consumers (Workers)              │
│  - EventConsumer.subscribe()            │
│  - Process events asynchronously        │
└─────────────────────────────────────────┘
```

### Event Publishing Example

```python
# In todo_routes.py - create_todo
@router.post("/", response_model=TodoResponse)
async def create_todo(todo: TodoCreate, ...):
    db_todo = Todo(**todo.model_dump(), user_id=current_user.id)
    session.add(db_todo)
    session.commit()
    
    # Publish event via EventService
    event_service = get_event_service()
    await event_service.publish_and_track(
        event_type=EventTypes.TASK_CREATED,
        aggregate_id=db_todo.id,
        aggregate_type='Task',
        user_id=current_user.id,
        payload={
            'id': str(db_todo.id),
            'title': db_todo.title,
            'created_at': db_todo.created_at.isoformat()
        },
        topic=KafkaTopics.TASKS_CREATED
    )
```

### Current Use Cases in Your App

| Use Case | Status | Description |
|----------|--------|-------------|
| **Event Sourcing** | ✅ Implemented | All domain events stored in `domain_events` table |
| **Audit Trail** | ✅ Implemented | Complete history of all changes |
| **Async Processing** | ⚠️ Partial | Events published but limited consumers |
| **Microservices Comm** | 🔧 Ready | Infrastructure ready for future services |
| **Real-time Analytics** | 🔧 Ready | Can track user behavior, task completion rates |

### Is Kafka Useful Here?

**YES** for:
- ✅ **Event Sourcing** - Complete audit trail of all task changes
- ✅ **Future Microservices** - Easy to add new services (notifications, analytics, ML)
- ✅ **Scalability** - Decouples services for horizontal scaling
- ✅ **Reliability** - Events persist even if consumers are down

**OVERKILL** for:
- ❌ **Simple CRUD** - Direct DB calls are simpler for basic operations
- ❌ **Low Traffic** - Single monolith doesn't need event streaming yet
- ❌ **Development** - Adds complexity during early development

**Recommendation:** Keep Kafka for event sourcing/audit trail, but consider using it more for async tasks as the app grows.

---

## 🔷 DAPR - Distributed Application Runtime

### Where Dapr Is Used

```
┌─────────────────────────────────────────────────────────────────┐
│                     DAPR SIDECAR ARCHITECTURE                    │
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   FastAPI   │    │   FastAPI   │    │   FastAPI   │         │
│  │    App      │    │    App      │    │    App      │         │
│  │  (Port 8001)│    │  (Port 8002)│    │  (Port 8003)│         │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                   ┌────────▼────────┐                           │
│                   │  Dapr Sidecar   │                           │
│                   │  (Port 3500)    │                           │
│                   └────────┬────────┘                           │
│                            │                                    │
│         ┌──────────────────┼──────────────────┐                 │
│         │                  │                  │                 │
│         ▼                  ▼                  ▼                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │  Pub/Sub    │   │  State      │   │  Secret     │           │
│  │  (Kafka)    │   │  (Redis)    │   │  Store      │           │
│  └─────────────┘   └─────────────┘   └─────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

### Dapr Components in Your App

#### 1. **Pub/Sub Messaging** (`backend/app/dapr/pubsub.py`)

```python
from dapr.clients import DaprClient

# Publish event
client.publish_event(
    pubsub_name="todo-pubsub",
    topic_name="todo.tasks.created",
    data=json.dumps(event_data)
)

# Subscribe to topic
@app.route('/events/tasks.created', methods=['POST'])
def handle_task_created():
    event = request.json
    # Process event
```

**Current Status:** ⚠️ **Partially Implemented** - Code exists but not actively used

#### 2. **State Management** (`backend/app/dapr/state.py`)

```python
from dapr.clients import DaprClient

# Save state
client.save_state(
    store_name="todo-state",
    key="user:uuid:preferences",
    value=json.dumps(preferences)
)

# Get state
result = client.get_state(
    store_name="todo-state",
    key="user:uuid:preferences"
)
```

**Current Status:** ❌ **Not Used** - PostgreSQL handles all state

### Is Dapr Useful Here?

**YES** for:
- ✅ **Multi-service deployment** - When you split into microservices
- ✅ **Service discovery** - Automatic service-to-service communication
- ✅ **State management abstraction** - Switch databases without code changes
- ✅ **Resiliency** - Built-in retry, circuit breaker, timeout policies
- ✅ **Observability** - Automatic tracing, metrics, logging

**NOT YET NEEDED** for:
- ❌ **Single monolith** - Your app is currently one FastAPI service
- ❌ **Simple state** - PostgreSQL handles all persistence needs
- ❌ **Local development** - Adds operational complexity

**Recommendation:** 
- **Short-term:** Dapr is overkill for current architecture
- **Long-term:** Valuable when you have multiple services (notification service, analytics service, ML service)

---

## 🏗️ WHEN TO USE EACH TECHNOLOGY

### Decision Matrix

```
┌─────────────────────┬──────────┬───────────┬──────────┬─────────┐
│ Use Case            │ Direct   │ Kafka     │ Dapr     │ Celery  │
│                     │ DB Call  │           │          │         │
├─────────────────────┼──────────┼───────────┼──────────┼─────────┤
│ Create Task         │ ✅ Yes   │ ⚠️ Audit  │ ❌ No    │ ❌ No   │
│ Update Task         │ ✅ Yes   │ ⚠️ Audit  │ ❌ No    │ ❌ No   │
│ Delete Task         │ ✅ Yes   │ ⚠️ Audit  │ ❌ No    │ ❌ No   │
│ Send Email Reminder │ ❌ No    │ ⚠️ Event  │ ❌ No    │ ✅ Yes  │
│ Generate Recurring  │ ❌ No    │ ⚠️ Event  │ ❌ No    │ ✅ Yes  │
│ Task                │          │           │          │         │
│ Audit Logging       │ ⚠️ Basic │ ✅ Full   │ ❌ No    │ ❌ No   │
│ Real-time Updates   │ ❌ No    │ ⚠️ Via WS │ ❌ No    │ ❌ No   │
│ Service-to-Service  │ ❌ No    │ ✅ Async  │ ✅ Sync  │ ❌ No   │
│ Communication       │          │           │          │         │
│ State Management    │ ✅ Yes   │ ❌ No     │ ⚠️ Over  │ ❌ No   │
│                     │          │           │  kill    │         │
└─────────────────────┴──────────┴───────────┴──────────┴─────────┘
```

### Recommended Architecture Evolution

#### **Phase 1: Current (Monolith)** ✅
```
FastAPI + PostgreSQL + Celery + WebSocket
├── Direct DB calls for CRUD
├── Celery for background tasks (reminders, recurring)
├── WebSocket for real-time updates
└── Kafka for event audit trail
```

#### **Phase 2: Growing (Event-Driven)** 🔄
```
FastAPI + PostgreSQL + Celery + Kafka + WebSocket
├── Direct DB calls for CRUD
├── Kafka events for ALL operations
├── Event consumers for:
│   ├── Search indexing
│   ├── Analytics
│   └── Notifications
└── Celery for time-based tasks
```

#### **Phase 3: Microservices** 🚀
```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Task      │  │   User      │  │   Chat      │
│   Service   │  │   Service   │  │   Service   │
│             │  │             │  │             │
│  FastAPI    │  │  FastAPI    │  │  FastAPI    │
│  + Dapr     │  │  + Dapr     │  │  + Dapr     │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
               ┌────────▼────────┐
               │  Kafka (Events) │
               │  Dapr (Pub/Sub) │
               └─────────────────┘
```

---

## 📋 SUMMARY & RECOMMENDATIONS

### Current State

| Component | Status | Usage |
|-----------|--------|-------|
| **Recurring Tasks** | ✅ Working | Celery Beat runs hourly |
| **Reminders** | ✅ Working | Celery Beat runs every minute |
| **Kafka** | ⚠️ Partial | Event publishing works, limited consumers |
| **Dapr** | ❌ Unused | Code exists but not integrated |
| **Celery** | ✅ Working | Background task processing |
| **WebSocket** | ✅ Working | Real-time task updates |

### Recommendations

#### **Immediate (Keep As Is)**
1. ✅ **Recurring Tasks** - Working well with Celery
2. ✅ **Reminders** - Working well with Celery
3. ✅ **Kafka for Audit** - Good for compliance/debugging
4. ✅ **WebSocket** - Perfect for real-time updates

#### **Short-term Improvements**
1. ⚠️ **Remove Dapr** - Adds complexity without benefit yet
2. ✅ **Enhance Kafka Consumers** - Add search indexing, analytics
3. ✅ **Monitor Celery** - Add monitoring for failed tasks

#### **Long-term (When Scaling)**
1. 🔄 **Re-evaluate Dapr** - When you have 3+ microservices
2. 🔄 **Kafka Streams** - For real-time analytics
3. 🔄 **Event Sourcing** - Full CQRS pattern if needed

### Bottom Line

**Your current architecture is solid!** 

- **Recurring tasks** and **reminders** work perfectly with Celery
- **Kafka** provides good audit trail foundation
- **Dapr** can be removed until you need microservices
- Focus on **features** not **infrastructure** at this stage

---

## 📁 Key Files Reference

### Recurring Tasks
- `backend/app/workers/recurring_worker.py` - Instance generation
- `backend/app/api/recurring_routes.py` - REST API
- `backend/app/models/recurring_task.py` - Data model
- `backend/app/workers/celery_app.py` - Schedule config

### Reminders
- `backend/app/workers/reminder_worker.py` - Email sending
- `backend/app/api/reminder_routes.py` - REST API
- `backend/app/models/reminder.py` - Data model
- `backend/app/services/email_service.py` - SMTP service

### Events (Kafka)
- `backend/app/events/publisher.py` - Kafka producer
- `backend/app/events/consumer.py` - Kafka consumer
- `backend/app/events/schemas.py` - Event schemas
- `backend/app/services/event_service.py` - Event orchestration
- `backend/app/models/event.py` - DomainEvent model

### Dapr
- `backend/app/dapr/pubsub.py` - Pub/sub wrapper
- `backend/app/dapr/state.py` - State management

### Celery
- `backend/app/workers/celery_app.py` - Main config
- `backend/app/workers/event_worker.py` - Event processing
