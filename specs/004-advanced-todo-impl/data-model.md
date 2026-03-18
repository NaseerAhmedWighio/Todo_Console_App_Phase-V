# Data Model: Advanced Todo Features Implementation

**Feature**: 004-advanced-todo-impl
**Date**: 2026-02-20
**Parent**: [Phase III Data Model](../003-advanced-todo-features/data-model.md)

---

## Overview

This document provides a focused summary of the data model for implementation. The complete data model with full entity definitions, validation rules, and schema is defined in the parent Phase III specification. This implementation-focused document highlights key relationships and workflows for reminders, recurring tasks, and due dates.

**Reference**: Complete entity definitions in `specs/003-advanced-todo-features/data-model.md`

---

## Entity Relationship Diagram

```
┌─────────────┐
│    User     │
│ - id        │
│ - timezone  │
│ - prefs     │
└──────┬──────┘
       │
       │ 1:N
       ▼
┌─────────────┐         ┌─────────────┐
│    Task     │◄───────►│   TaskTag   │
│ - id        │         │ - task_id   │
│ - user_id   │         │ - tag_id    │
│ - priority  │         └──────┬──────┘
│ - due_date  │                │
│ - status    │                │
│ - ...       │         ┌──────▼──────┐
└──────┬──────┘         │    Tag      │
       │                │ - id        │
       │ 1:1            │ - user_id   │
       │                │ - name      │
       ▼                │ - color     │
┌─────────────┐         └─────────────┘
│  Reminder   │
│ - id        │
│ - task_id   │
│ - timing    │
│ - channel   │
│ - status    │
└─────────────┘

┌─────────────┐
│RecurringTask│
│ - id        │
│ - task_id   │
│ - pattern   │
│ - interval  │
│ - end_cond  │
│ - next_due  │
└─────────────┘
       │
       │ 1:N (generates)
       ▼
┌─────────────┐
│    Task     │ (instances)
└─────────────┘

┌─────────────┐
│DomainEvent  │
│ - id        │
│ - type      │
│ - payload   │
│ - user_id   │
│ - published │
└─────────────┘
```

---

## Key Entity Workflows

### 1. Recurring Task Workflow

```
User creates recurring task
         │
         ▼
┌─────────────────┐
│ Create Task     │ (base task with is_recurring=false)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Create          │ (recurring pattern configuration)
│ RecurringTask   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Calculate       │ (using dateutil.rrule)
│ next_due_date   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Store in DB     │ (PostgreSQL)
└────────┬────────┘
         │
         │ Background Worker (hourly)
         ▼
┌─────────────────┐
│ Check           │ (WHERE is_active AND next_due <= NOW)
│ due recurring   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate new    │ (clone base task)
│ Task instance   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Update          │ (calculate next occurrence)
│ RecurringTask   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Publish event   │ (recurring.instance_generated)
└─────────────────┘
```

### 2. Reminder Workflow

```
User sets reminder on task
         │
         ▼
┌─────────────────┐
│ Validate task   │ (must have due_date)
│ has due_date    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Calculate       │ (due_date - timing)
│ scheduled_time  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Create Reminder │ (status='pending')
│ in PostgreSQL   │
└────────┬────────┘
         │
         │ Background Worker (every minute)
         ▼
┌─────────────────┐
│ Query pending   │ (WHERE status='pending' AND scheduled_time <= NOW)
│ reminders       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Deliver         │ (in-app, email, web_push)
│ notification    │
└────────┬────────┘
         │
         ├─────────────┐
         │             │
         ▼             ▼
┌─────────────┐ ┌─────────────┐
│ Success     │ │ Failure     │
└──────┬──────┘ └──────┬──────┘
       │               │
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│ status='sent'│ │ Retry with  │
└─────────────┘ │ backoff     │
                └─────────────┘
```

### 3. Due Date and Overdue Detection

```
Task with due_date stored in UTC
         │
         ▼
┌─────────────────┐
│ Compare with    │ (NOW() in UTC)
│ current time    │
└────────┬────────┘
         │
         ├──────────────┬──────────────┐
         │              │              │
         ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ due_date >  │ │ due_date <= │ │ completed   │
│ NOW()       │ │ NOW()       │ │ before due  │
│             │ │             │ │             │
│ Upcoming    │ │ Overdue     │ │ On time     │
└─────────────┘ └─────────────┘ └─────────────┘
     │                │                │
     │                │                │
     ▼                ▼                ▼
  Normal          Red styling     Normal
  display         indicator       display
```

---

## Database Indexes for Performance

### Critical Indexes (Must Create)

```sql
-- Task filtering and sorting
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_user_due_date ON tasks(user_id, due_date);
CREATE INDEX idx_tasks_user_status_priority ON tasks(user_id, is_completed, priority);

-- Reminder processing (partial index for pending only)
CREATE INDEX idx_reminders_pending ON reminders(status, scheduled_time)
    WHERE status = 'pending';

-- Recurring task generation (partial index for active only)
CREATE INDEX idx_recurring_tasks_next_due ON recurring_tasks(next_due_date)
    WHERE is_active = TRUE;

-- Full-text search (GIN index)
CREATE INDEX idx_tasks_search_vector ON tasks USING GIN (search_vector);

-- Tag filtering
CREATE INDEX idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag_id ON task_tags(tag_id);

-- Event publishing (partial index for unpublished)
CREATE INDEX idx_domain_events_unpublished ON domain_events(published, created_at)
    WHERE published = FALSE;
```

---

## State Transitions

### Reminder Status Transitions

```
┌──────────┐
│ pending  │◄────────────────┐
└────┬─────┘                 │
     │                        │
     ├────────────────┐       │
     │                │       │
     ▼                ▼       │
┌──────────┐    ┌──────────┐  │
│  sent    │    │  failed  │──┘ (retry)
└──────────┘    └────┬─────┘
                     │
                     ▼
               ┌──────────┐
               │ cancelled│ (max retries or task completed)
               └──────────┘
```

### Domain Event State Transitions

```
┌──────────┐
│ created  │
└────┬─────┘
     │
     ▼
┌──────────┐
│ published│ (sent to Kafka)
└────┬─────┘
     │
     ▼
┌──────────┐
│ processed│ (consumer handled)
└──────────┘
```

---

## Data Access Patterns

### 1. Get Tasks with Filters and Sort

```sql
SELECT * FROM tasks
WHERE user_id = :user_id
  AND (:status IS NULL OR is_completed = :status)
  AND (:priority IS NULL OR priority = :priority)
  AND (:tag_id IS NULL OR id IN (
      SELECT task_id FROM task_tags WHERE tag_id = :tag_id
  ))
  AND (:due_date_from IS NULL OR due_date >= :due_date_from)
  AND (:due_date_to IS NULL OR due_date <= :due_date_to)
ORDER BY
  CASE :sort_by
    WHEN 'due_date' THEN due_date
    WHEN 'priority' THEN
      CASE priority
        WHEN 'urgent' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
      END
    WHEN 'created_at' THEN created_at
    WHEN 'title' THEN title
  END
  CASE :sort_order
    WHEN 'asc' THEN ASC
    ELSE DESC
  END
LIMIT :limit OFFSET :offset;
```

### 2. Search Tasks with Full-Text

```sql
SELECT *, ts_rank(search_vector, query) AS rank
FROM tasks, plainto_tsquery('english', :search_query) query
WHERE user_id = :user_id
  AND search_vector @@ query
ORDER BY rank DESC
LIMIT 50;
```

### 3. Get Pending Reminders (Worker Query)

```sql
SELECT r.*, t.title, t.due_date, t.user_id
FROM reminders r
JOIN tasks t ON r.task_id = t.id
WHERE r.status = 'pending'
  AND r.scheduled_time <= NOW()
ORDER BY r.scheduled_time ASC
LIMIT 100;
```

### 4. Get Recurring Tasks Due for Generation

```sql
SELECT * FROM recurring_tasks
WHERE is_active = TRUE
  AND (next_due_date IS NULL OR next_due_date <= NOW())
ORDER BY next_due_date ASC;
```

### 5. Get Unpublished Events

```sql
SELECT * FROM domain_events
WHERE published = FALSE
ORDER BY created_at ASC
LIMIT 100;
```

---

## Migration Checklist

### Phase 1: Add New Tables
- [ ] Create `tags` table
- [ ] Create `task_tags` join table
- [ ] Create `reminders` table
- [ ] Create `recurring_tasks` table
- [ ] Create `domain_events` table
- [ ] Create all indexes

### Phase 2: Extend Existing Tables
- [ ] Add `priority`, `due_date`, `timezone`, `is_recurring`, `recurring_task_id` to `tasks`
- [ ] Add `timezone`, `notification_preferences`, `default_task_priority` to `users`
- [ ] Add `search_vector` column to `tasks`
- [ ] Create trigger for `search_vector` auto-update

### Phase 3: Dapr State Table
- [ ] Create `dapr_state` table for Dapr state management

---

## Implementation Notes

### Timezone Handling

- **Storage**: All datetime values stored in UTC
- **User preference**: Timezone stored in `users.timezone` and `tasks.timezone`
- **Display**: Convert UTC to user's local timezone at presentation layer
- **Calculation**: Use `pytz` for timezone conversions

### Search Vector Maintenance

```sql
-- Trigger to auto-update search_vector on task changes
CREATE TRIGGER tsvectorupdate
  BEFORE UPDATE OR INSERT ON tasks
  FOR EACH ROW EXECUTE FUNCTION tasks_search_vector_update();
```

### Cascade Delete Behavior

- Deleting a **user** cascades to: tasks, tags, reminders, recurring_tasks, domain_events
- Deleting a **task** cascades to: task_tags, reminders
- Deleting a **tag** cascades to: task_tags
- Deleting a **recurring task** cascades to: generated task instances

---

## References

- Full entity definitions: `specs/003-advanced-todo-features/data-model.md`
- Research findings: `specs/004-advanced-todo-impl/research.md`
- API contracts: `specs/004-advanced-todo-impl/contracts/`
