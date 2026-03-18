# Research & Discovery: Advanced Todo Features Implementation

**Feature**: 004-advanced-todo-impl
**Date**: 2026-02-20
**Input**: Technical context from [plan.md](plan.md)

---

## Overview

This research document addresses key technical decisions for implementing reminders, recurring tasks, and due dates with proper database integration. All findings inform the design decisions in subsequent phases.

---

## Research Topic 1: Recurring Task Date Calculation Algorithms

**Question**: How do we accurately calculate recurring task instances while handling edge cases?

### Decision: Use python-dateutil.rrule with custom wrapper

**Rationale**:
- python-dateutil.rrule implements RFC 5545 iCalendar recurrence rules
- Handles complex edge cases automatically (month-end dates, leap years, timezone transitions)
- Well-tested, mature library with excellent documentation
- Supports all required patterns: daily, weekly, monthly, yearly, custom intervals
- Timezone-aware with pytz/zoneinfo integration

**Alternatives Considered**:
- **Custom recurrence engine**: More control but error-prone for edge cases
- **recurrence library**: Lighter weight but less feature-complete
- **django-recurrence**: Tied to Django, not compatible with FastAPI

### Edge Case Handling Strategy

**Month-end dates** (e.g., monthly on the 31st):
```python
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime

# When the 31st doesn't exist in a month, dateutil rolls to last day
rrule(MONTHLY, dtstart=datetime(2024, 1, 31), count=3)
# Results: Jan 31, Feb 29 (leap year), Mar 31
```

**Leap year handling**:
```python
# Yearly on Feb 29 - only occurs in leap years
rrule(YEARLY, dtstart=datetime(2024, 2, 29), count=5)
# Results: 2024-02-29, 2028-02-29, 2032-02-29, ...
```

**Timezone transitions** (DST):
```python
import pytz
from dateutil.rrule import rrule, DAILY

tz = pytz.timezone('America/New_York')
dtstart = tz.localize(datetime(2024, 3, 9, 10, 0))  # Before DST

# dateutil handles DST transition automatically
rrule(DAILY, dtstart=dtstart, count=5)
```

### Implementation Pattern

```python
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY
from datetime import datetime
import pytz

class RecurringService:
    def calculate_next_occurrence(
        self,
        pattern: str,
        interval: int,
        start_date: datetime,
        timezone: str = 'UTC',
        by_weekday: str = None,
        by_monthday: int = None,
        by_month: str = None
    ) -> datetime:
        """Calculate next occurrence based on recurrence pattern"""
        tz = pytz.timezone(timezone)
        
        # Map pattern to dateutil constant
        freq_map = {
            'daily': DAILY,
            'weekly': WEEKLY,
            'monthly': MONTHLY,
            'yearly': YEARLY
        }
        
        rule = rrule(
            freq=freq_map[pattern],
            interval=interval,
            dtstart=start_date,
            byweekday=self._parse_weekdays(by_weekday) if by_weekday else None,
            bymonthday=by_monthday,
            bymonth=self._parse_months(by_month) if by_month else None,
            count=2  # Get next occurrence after start_date
        )
        
        occurrences = list(rule)
        return occurrences[1] if len(occurrences) > 1 else None
```

---

## Research Topic 2: Reminder Scheduling and Delivery System

**Question**: How do we schedule and deliver reminders reliably with retry logic?

### Decision: Celery workers with Redis broker + PostgreSQL state

**Rationale**:
- Celery provides mature, scalable task scheduling
- Redis broker offers fast, reliable message queuing
- PostgreSQL persistence ensures reminders survive restarts
- Built-in retry logic with exponential backoff
- Supports distributed deployment across multiple workers

**Alternatives Considered**:
- **APScheduler**: Simpler but less scalable, single-instance focused
- **RQ (Redis Queue)**: Redis-only, less feature-rich than Celery
- **AWS SQS + Lambda**: External dependency, vendor lock-in

### Reminder Scheduling Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  PostgreSQL     │────▶│  Celery      │────▶│  Notification   │
│  (reminders)    │     │  Worker      │     │  Service        │
└─────────────────┘     └──────────────┘     └─────────────────┘
       │                       │                      │
       │ 1. Query pending      │ 2. Process          │ 3. Deliver
       │    reminders          │    reminder          │    notification
       │                       │                      │
       │◀──────────────────────┴──────────────────────┘
       │ 4. Update status (sent/failed)
```

### Retry Strategy

```python
from celery import Celery
from celery.utils.log import get_task_logger

app = Celery('reminder_worker', broker='redis://localhost:6379/0')

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_reminder(self, reminder_id: str):
    """Send reminder with exponential backoff retry"""
    try:
        reminder = get_reminder(reminder_id)
        
        # Deliver notification
        if reminder.delivery_channel == 'in_app':
            _send_in_app_notification(reminder)
        elif reminder.delivery_channel == 'email':
            _send_email_notification(reminder)
        
        # Mark as sent
        update_reminder_status(reminder_id, 'sent')
        
    except Exception as exc:
        # Retry with exponential backoff: 60s, 120s, 240s
        raise self.retry(exc, countdown=60 * (2 ** self.request.retries))
```

### Reminder Timing Calculation

```python
from datetime import datetime, timedelta

def calculate_scheduled_time(
    due_date: datetime,
    timing_minutes: int = 0,
    timing_days: int = None
) -> datetime:
    """Calculate when reminder should be sent"""
    if timing_days is not None and timing_days > 0:
        return due_date - timedelta(days=timing_days)
    else:
        return due_date - timedelta(minutes=timing_minutes)

# Examples:
# Due: 2024-02-20 14:00, Reminder: 15 minutes before
# Scheduled: 2024-02-20 13:45

# Due: 2024-02-20 14:00, Reminder: 1 day before
# Scheduled: 2024-02-19 14:00
```

### Database Query for Pending Reminders

```sql
-- Get reminders due for processing (run every minute)
SELECT r.*, t.title, t.due_date, t.user_id
FROM reminders r
JOIN tasks t ON r.task_id = t.id
WHERE r.status = 'pending'
  AND r.scheduled_time <= NOW()
ORDER BY r.scheduled_time ASC
LIMIT 100;
```

---

## Research Topic 3: Due Date Timezone Handling

**Question**: How do we handle due dates across different timezones correctly?

### Decision: Store in UTC, display in user's timezone

**Rationale**:
- UTC storage ensures consistency across database and services
- User timezone preference stored in profile
- Conversion happens at presentation layer
- Avoids DST ambiguity and timezone drift

**Implementation Pattern**:

```python
import pytz
from datetime import datetime

class TaskService:
    def create_task(
        self,
        user_id: str,
        title: str,
        due_date: datetime = None,
        timezone: str = 'UTC'
    ):
        """Create task with timezone-aware due date"""
        tz = pytz.timezone(timezone)
        
        # Convert user's local time to UTC for storage
        if due_date:
            # Assume due_date is in user's timezone
            if due_date.tzinfo is None:
                due_date = tz.localize(due_date)
            due_date_utc = due_date.astimezone(pytz.UTC)
        else:
            due_date_utc = None
        
        task = Todo(
            user_id=user_id,
            title=title,
            due_date=due_date_utc,
            timezone=timezone
        )
        save_task(task)
        return task
    
    def get_due_date_display(self, task: Todo) -> str:
        """Convert UTC due date to user's local time for display"""
        if not task.due_date:
            return None
        
        tz = pytz.timezone(task.timezone or 'UTC')
        local_time = task.due_date.astimezone(tz)
        return local_time.strftime('%Y-%m-%d %H:%M')
```

### Overdue Detection Logic

```python
from datetime import datetime, timezone

def is_overdue(task: Todo) -> bool:
    """Check if task is overdue"""
    if not task.due_date or task.is_completed:
        return False
    
    # Compare in UTC
    now_utc = datetime.now(timezone.utc)
    return task.due_date < now_utc
```

---

## Research Topic 4: Full-Text Search with PostgreSQL

**Question**: How do we implement fast, relevant search across tasks?

### Decision: PostgreSQL tsvector with GIN index

**Rationale**:
- No additional infrastructure (uses existing PostgreSQL)
- GIN indexes provide fast search (<100ms for 10k tasks)
- Built-in relevance ranking with ts_rank()
- Supports stemming, stop words, multiple languages

### Search Implementation

```python
from sqlalchemy import text

class SearchService:
    def search_tasks(
        self,
        user_id: str,
        query: str,
        priority: str = None,
        status: str = None,
        tag_id: str = None,
        limit: int = 50
    ):
        """Full-text search with filters"""
        search_query = text("""
            SELECT t.*, ts_rank(t.search_vector, plainto_tsquery('english', :query)) AS rank
            FROM tasks t
            WHERE t.user_id = :user_id
              AND t.search_vector @@ plainto_tsquery('english', :query)
              AND (:priority IS NULL OR t.priority = :priority)
              AND (:status IS NULL OR t.is_completed = :status::boolean)
              AND (:tag_id IS NULL OR t.id IN (
                  SELECT task_id FROM task_tags WHERE tag_id = :tag_id
              ))
            ORDER BY rank DESC
            LIMIT :limit
        """)
        
        results = db.execute(
            search_query,
            {
                'user_id': user_id,
                'query': query,
                'priority': priority,
                'status': status,
                'tag_id': tag_id,
                'limit': limit
            }
        )
        return results.all()
```

### Search Vector Update Trigger

```sql
-- Automatically update search_vector when task changes
CREATE OR REPLACE FUNCTION tasks_search_vector_update() RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(NEW.description, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(NEW.priority, '')), 'C');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER tsvectorupdate
  BEFORE UPDATE OR INSERT ON tasks
  FOR EACH ROW EXECUTE FUNCTION tasks_search_vector_update();
```

---

## Research Topic 5: Kafka Event Publishing Patterns

**Question**: How do we publish events reliably without blocking user requests?

### Decision: Async event publishing with retry queue

**Rationale**:
- Non-blocking: events published asynchronously
- Retry queue handles transient failures
- Event sourcing pattern for audit trail
- Decouples services for scalability

### Event Publishing Pattern

```python
from kafka import KafkaProducer
import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class EventPublisher:
    def __init__(self, bootstrap_servers: list):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',  # Wait for all replicas to acknowledge
            retries=3,
            retry_backoff_ms=100
        )
    
    def publish(self, event_type: str, payload: Dict[str, Any], user_id: str):
        """Publish event to Kafka topic"""
        event = {
            'event_type': event_type,
            'payload': payload,
            'user_id': user_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        topic = f'todo.{event_type}'  # e.g., todo.task.created
        
        try:
            future = self.producer.send(topic, value=event)
            # Don't block - fire and forget
            # future.get(timeout=10)  # Optional: wait for confirmation
        except Exception as e:
            logger.error(f'Failed to publish event {event_type}: {e}')
            # Store in database for later retry
            self._store_failed_event(event)
    
    def _store_failed_event(self, event: Dict[str, Any]):
        """Store failed event in database for retry"""
        # Insert into domain_events table with published=False
        pass
```

### Event Topics Structure

```
todo.task.created        - Task creation events
todo.task.updated        - Task update events
todo.task.completed      - Task completion events
todo.task.deleted        - Task deletion events
todo.reminder.sent       - Reminder delivery events
todo.recurring.generated - Recurring instance generation events
```

---

## Research Topic 6: Dapr State Management Integration

**Question**: How do we use Dapr for state management and pub/sub?

### Decision: Dapr Python SDK with PostgreSQL state store

**Rationale**:
- Official Dapr SDK provides simple API
- PostgreSQL state store integrates with existing database
- Pub/sub abstraction works with multiple brokers (Kafka, Redis, etc.)
- Service-to-service communication handled automatically

### Dapr State Management Pattern

```python
from dapr.clients import DaprClient
import json

class DaprStateManager:
    def __init__(self, store_name: str = 'statestore'):
        self.store_name = store_name
    
    def save_state(self, key: str, value: dict):
        """Save state to Dapr state store"""
        with DaprClient() as client:
            client.save_state(
                store_name=self.store_name,
                key=key,
                value=json.dumps(value)
            )
    
    def get_state(self, key: str) -> dict:
        """Retrieve state from Dapr state store"""
        with DaprClient() as client:
            result = client.get_state(store_name=self.store_name, key=key)
            return json.loads(result.data) if result.data else None
    
    def delete_state(self, key: str):
        """Delete state from Dapr state store"""
        with DaprClient() as client:
            client.delete_state(store_name=self.store_name, key=key)
```

### Dapr Pub/Sub Pattern

```python
from dapr.clients import DaprClient
import json

class DaprPubSub:
    def __init__(self, pubsub_name: str = 'pubsub'):
        self.pubsub_name = pubsub_name
    
    def publish(self, topic: str, data: dict):
        """Publish event to Dapr pub/sub"""
        with DaprClient() as client:
            client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=topic,
                data=json.dumps(data)
            )
    
    def subscribe(self, topic: str, handler):
        """Subscribe to topic (decorator pattern)"""
        from dapr.ext.fastapi import DaprApp
        return DaprApp.subscribe(topic, handler)
```

### Dapr Component Configuration

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
    value: "postgresql://user:pass@neon-host:5432/dbname?sslmode=require"
```

---

## Research Topic 7: Tag Management System Design

**Question**: How do we design an efficient tag system with many-to-many relationships?

### Decision: Many-to-many with join table + per-user uniqueness

**Rationale**:
- Standard relational pattern for many-to-many
- Efficient queries with proper indexes
- Per-user tag name uniqueness prevents duplicates
- Cascade deletes maintain referential integrity

### Tag Assignment Pattern

```python
class TagService:
    def create_tag(self, user_id: str, name: str, color: str = '#6B7280'):
        """Create tag with uniqueness validation"""
        # Check for duplicate (case-insensitive)
        existing = db.query(Tag).filter(
            Tag.user_id == user_id,
            Tag.name.ilike(name)
        ).first()
        
        if existing:
            raise ValueError(f'Tag "{name}" already exists')
        
        tag = Tag(user_id=user_id, name=name, color=color)
        db.add(tag)
        db.commit()
        return tag
    
    def assign_tag_to_task(self, task_id: str, tag_id: str):
        """Assign tag to task"""
        # Check if already assigned
        existing = db.query(TaskTag).filter(
            TaskTag.task_id == task_id,
            TaskTag.tag_id == tag_id
        ).first()
        
        if existing:
            return  # Already assigned
        
        assignment = TaskTag(task_id=task_id, tag_id=tag_id)
        db.add(assignment)
        db.commit()
    
    def get_tasks_by_tag(self, user_id: str, tag_id: str):
        """Get all tasks with a specific tag"""
        return db.query(Todo).join(TaskTag).filter(
            Todo.user_id == user_id,
            TaskTag.tag_id == tag_id
        ).all()
```

---

## Summary of Decisions

| Topic | Decision | Key Library/Tool |
|-------|----------|------------------|
| Recurring date calculation | python-dateutil.rrule | dateutil, pytz |
| Reminder scheduling | Celery workers with Redis | Celery, Redis |
| Due date timezone | Store UTC, display local | pytz |
| Full-text search | PostgreSQL tsvector + GIN | PostgreSQL |
| Event publishing | Async Kafka publishing | kafka-python |
| State management | Dapr SDK + PostgreSQL | dapr-sdk |
| Tag system | Many-to-many join table | SQLModel |

---

## Next Steps

1. **Phase 1 Design**: Use these decisions to create data-model.md
2. **API Contracts**: Define endpoints based on service patterns
3. **Quick Start**: Document setup for Kafka, Dapr, Celery, Redis
