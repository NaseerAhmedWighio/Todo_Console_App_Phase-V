# Data Model: Advanced Todo Features - Phase III

**Feature**: 003-advanced-todo-features  
**Date**: 2026-02-19  
**Parent**: [Phase II Data Model](../002-todo-fullstack/data-model.md)

---

## Overview

This document extends the Phase II data model with new entities and attributes required for advanced todo features: recurring tasks, reminders, priorities, tags, search, and event tracking. All existing Phase II entities are preserved for backward compatibility.

---

## New Entities

### Entity: Tag

User-defined labels for organizing tasks with flexible categorization.

#### Attributes

- **id** (UUID, Primary Key)
  - Type: UUID
  - Required: Yes
  - Unique: Yes
  - Description: Unique identifier for the tag

- **user_id** (UUID, Foreign Key)
  - Type: UUID
  - Required: Yes
  - Reference: users.id
  - Description: ID of the user who owns this tag
  - Index: Yes (idx_tags_user_id)

- **name** (String)
  - Type: String (max 50 characters)
  - Required: Yes
  - Unique: Yes (per user)
  - Validation: Alphanumeric + spaces, no special characters
  - Description: Display name of the tag

- **color** (String)
  - Type: String (7 characters, hex color code)
  - Required: No
  - Default: '#6B7280' (gray)
  - Validation: Valid hex color format (#RRGGBB)
  - Description: Visual color for the tag

- **created_at** (DateTime)
  - Type: DateTime
  - Required: Yes
  - Default: Current timestamp
  - Description: Timestamp when the tag was created

#### Relationships

- One Tag belongs to one User (many-to-one)
- One Tag can be assigned to many Tasks (many-to-many via TaskTag)

#### Validation Rules

- Tag name must be unique per user (case-insensitive)
- Tag name must be 1-50 characters
- Color must be valid hex format (#RRGGBB)
- Users can only access their own tags

---

### Entity: TaskTag (Join Table)

Many-to-many relationship between tasks and tags.

#### Attributes

- **task_id** (UUID, Foreign Key)
  - Type: UUID
  - Required: Yes
  - Reference: tasks.id
  - Description: ID of the task

- **tag_id** (UUID, Foreign Key)
  - Type: UUID
  - Required: Yes
  - Reference: tags.id
  - Description: ID of the tag

- **created_at** (DateTime)
  - Type: DateTime
  - Required: Yes
  - Default: Current timestamp
  - Description: Timestamp when tag was assigned to task

#### Relationships

- Composite primary key: (task_id, tag_id)
- Cascade delete: If task or tag is deleted, remove the assignment

#### Validation Rules

- Each task-tag combination must be unique
- Both task and tag must belong to the same user

---

### Entity: Reminder

Scheduled notifications for tasks with configurable timing and delivery channels.

#### Attributes

- **id** (UUID, Primary Key)
  - Type: UUID
  - Required: Yes
  - Unique: Yes
  - Description: Unique identifier for the reminder

- **task_id** (UUID, Foreign Key)
  - Type: UUID
  - Required: Yes
  - Reference: tasks.id
  - Description: ID of the task this reminder is for
  - Index: Yes (idx_reminders_task_id)

- **timing_minutes** (Integer)
  - Type: Integer
  - Required: Yes
  - Default: 0
  - Validation: >= 0 (minutes before due date)
  - Description: Number of minutes before due date to send reminder

- **timing_days** (Integer)
  - Type: Integer
  - Required: No
  - Validation: >= 0 (days before due date, alternative to minutes)
  - Description: Number of days before due date to send reminder

- **delivery_channel** (String)
  - Type: String (max 20 characters)
  - Required: Yes
  - Validation: One of: 'in_app', 'email', 'web_push', 'sms'
  - Default: 'in_app'
  - Description: Channel through which to deliver the reminder

- **scheduled_time** (DateTime)
  - Type: DateTime
  - Required: Yes
  - Description: Calculated time when reminder should be sent (derived from due_date - timing)

- **sent_at** (DateTime)
  - Type: DateTime
  - Required: No
  - Description: Timestamp when reminder was actually sent (null if not yet sent)

- **status** (String)
  - Type: String (max 20 characters)
  - Required: Yes
  - Default: 'pending'
  - Validation: One of: 'pending', 'sent', 'failed', 'cancelled'
  - Description: Current status of the reminder

- **error_message** (Text)
  - Type: Text (optional)
  - Required: No
  - Description: Error message if delivery failed

- **created_at** (DateTime)
  - Type: DateTime
  - Required: Yes
  - Default: Current timestamp
  - Description: Timestamp when the reminder was created

#### Relationships

- One Reminder belongs to one Task (many-to-one)
- One Task can have many Reminders

#### Validation Rules

- Task must have a due_date to create a reminder
- Either timing_minutes or timing_days must be provided
- scheduled_time is calculated automatically from due_date and timing
- Users can only access reminders for their own tasks

---

### Entity: RecurringTask

Extension of Task with recurrence pattern configuration.

#### Attributes

- **id** (UUID, Primary Key)
  - Type: UUID
  - Required: Yes
  - Unique: Yes
  - Description: Unique identifier for the recurring task series

- **series_id** (UUID)
  - Type: UUID
  - Required: No
  - Description: ID of the parent series (null for original, set for instances)
  - Index: Yes (idx_recurring_series_id)

- **task_id** (UUID, Foreign Key)
  - Type: UUID
  - Required: Yes
  - Reference: tasks.id
  - Description: ID of the base task
  - Index: Yes (idx_recurring_task_id)

- **recurrence_pattern** (String)
  - Type: String (max 50 characters)
  - Required: Yes
  - Validation: One of: 'daily', 'weekly', 'monthly', 'yearly', 'custom'
  - Description: Type of recurrence pattern

- **interval** (Integer)
  - Type: Integer
  - Required: Yes
  - Default: 1
  - Validation: >= 1
  - Description: Recur every N units (e.g., every 2 weeks = interval 2)

- **by_weekday** (String)
  - Type: String (max 50 characters, comma-separated)
  - Required: No
  - Validation: Comma-separated integers 0-6 (0=Monday, 6=Sunday)
  - Example: "0,2,4" = Monday, Wednesday, Friday
  - Description: Specific weekdays for weekly recurrence

- **by_monthday** (Integer)
  - Type: Integer
  - Required: No
  - Validation: 1-31
  - Description: Day of month for monthly recurrence

- **by_month** (String)
  - Type: String (max 50 characters, comma-separated)
  - Required: No
  - Validation: Comma-separated integers 1-12
  - Example: "1,4,7,10" = Jan, Apr, Jul, Oct
  - Description: Specific months for yearly recurrence

- **end_condition** (String)
  - Type: String (max 20 characters)
  - Required: Yes
  - Default: 'never'
  - Validation: One of: 'never', 'after_occurrences', 'on_date'
  - Description: When the recurrence should end

- **end_occurrences** (Integer)
  - Type: Integer
  - Required: No
  - Validation: >= 1
  - Description: End after this many occurrences (if end_condition = 'after_occurrences')

- **end_date** (DateTime)
  - Type: DateTime
  - Required: No
  - Description: End on this specific date (if end_condition = 'on_date')

- **last_generated_date** (DateTime)
  - Type: DateTime
  - Required: No
  - Description: Date when the last task instance was generated

- **next_due_date** (DateTime)
  - Type: DateTime
  - Required: No
  - Description: Calculated next due date for the recurring task

- **is_active** (Boolean)
  - Type: Boolean
  - Required: Yes
  - Default: True
  - Description: Whether the recurring series is still active

- **created_at** (DateTime)
  - Type: DateTime
  - Required: Yes
  - Default: Current timestamp
  - Description: Timestamp when the recurring task was created

#### Relationships

- One RecurringTask extends one Task (one-to-one)
- One RecurringTask can generate many Task instances

#### Validation Rules

- Recurrence pattern must be valid
- Interval must be >= 1
- by_weekday, by_monthday, by_month must match the recurrence_pattern
- end_occurrences required if end_condition = 'after_occurrences'
- end_date required if end_condition = 'on_date'
- Users can only access their own recurring tasks

---

### Entity: DomainEvent

Event record for event-driven architecture, tracking all task operations.

#### Attributes

- **id** (UUID, Primary Key)
  - Type: UUID
  - Required: Yes
  - Unique: Yes
  - Description: Unique identifier for the event

- **event_type** (String)
  - Type: String (max 50 characters)
  - Required: Yes
  - Validation: One of: 'task.created', 'task.updated', 'task.completed', 'task.deleted', 'task.reminder_sent', 'recurring.instance_generated'
  - Description: Type of event that occurred
  - Index: Yes (idx_events_type)

- **aggregate_id** (UUID)
  - Type: UUID
  - Required: Yes
  - Description: ID of the aggregate root (e.g., task_id)
  - Index: Yes (idx_events_aggregate)

- **aggregate_type** (String)
  - Type: String (max 50 characters)
  - Required: Yes
  - Description: Type of aggregate (e.g., 'Task', 'RecurringTask')

- **user_id** (UUID)
  - Type: UUID
  - Required: Yes
  - Description: ID of the user who triggered the event
  - Index: Yes (idx_events_user_id)

- **payload** (JSON)
  - Type: JSON
  - Required: Yes
  - Description: Event payload containing relevant data
  - Example: {"title": "Buy groceries", "priority": "high"}

- **metadata** (JSON)
  - Type: JSON (optional)
  - Required: No
  - Description: Additional metadata (timestamp, version, correlation_id)

- **published** (Boolean)
  - Type: Boolean
  - Required: Yes
  - Default: False
  - Description: Whether the event has been published to Kafka

- **published_at** (DateTime)
  - Type: DateTime
  - Required: No
  - Description: Timestamp when event was published

- **processed** (Boolean)
  - Type: Boolean
  - Required: Yes
  - Default: False
  - Description: Whether the event has been processed by consumers

- **processed_at** (DateTime)
  - Type: DateTime
  - Required: No
  - Description: Timestamp when event was processed

- **error_message** (Text)
  - Type: Text (optional)
  - Required: No
  - Description: Error message if processing failed

- **created_at** (DateTime)
  - Type: DateTime
  - Required: Yes
  - Default: Current timestamp
  - Description: Timestamp when the event occurred

#### Relationships

- One DomainEvent is associated with one User
- One DomainEvent is associated with one aggregate (Task, RecurringTask, etc.)

#### Validation Rules

- event_type must be from the allowed set
- payload must be valid JSON
- user_id must reference a valid user
- Events are immutable once created

---

## Extended Entities (Phase II Modifications)

### Entity: Task (Extended)

The existing Task entity is extended with new attributes for advanced features.

#### New Attributes Added

- **priority** (String)
  - Type: String (max 20 characters)
  - Required: Yes
  - Default: 'medium'
  - Validation: One of: 'low', 'medium', 'high', 'urgent'
  - Description: Priority level of the task
  - Index: Yes (idx_tasks_priority)

- **due_date** (DateTime)
  - Type: DateTime
  - Required: No
  - Description: Due date and time for the task
  - Index: Yes (idx_tasks_due_date)

- **timezone** (String)
  - Type: String (max 50 characters)
  - Required: No
  - Default: 'UTC'
  - Validation: Valid IANA timezone name (e.g., 'America/New_York')
  - Description: User's timezone for date/time calculations

- **is_recurring** (Boolean)
  - Type: Boolean
  - Required: Yes
  - Default: False
  - Description: Whether this task is part of a recurring series
  - Index: Yes (idx_tasks_is_recurring)

- **recurring_task_id** (UUID, Foreign Key)
  - Type: UUID
  - Required: No
  - Reference: recurring_task.id
  - Description: ID of the parent recurring task (if is_recurring = true)
  - Index: Yes (idx_tasks_recurring_id)

#### Modified Indexes

```sql
-- New indexes for advanced features
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_is_recurring ON tasks(is_recurring);
CREATE INDEX idx_tasks_recurring_id ON tasks(recurring_task_id);
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_user_due_date ON tasks(user_id, due_date);
CREATE INDEX idx_tasks_user_status_priority ON tasks(user_id, is_completed, priority);
```

---

### Entity: User (Extended)

The existing User entity is extended with new attributes for preferences.

#### New Attributes Added

- **timezone** (String)
  - Type: String (max 50 characters)
  - Required: Yes
  - Default: 'UTC'
  - Validation: Valid IANA timezone name
  - Description: User's preferred timezone for date/time operations

- **notification_preferences** (JSON)
  - Type: JSON
  - Required: No
  - Default: {"in_app": true, "email": false, "web_push": false, "sms": false}
  - Description: User's preferences for notification channels

- **default_task_priority** (String)
  - Type: String (max 20 characters)
  - Required: No
  - Default: 'medium'
  - Validation: One of: 'low', 'medium', 'high', 'urgent'
  - Description: Default priority for new tasks

#### Example notification_preferences JSON

```json
{
  "in_app": true,
  "email": true,
  "web_push": false,
  "sms": false,
  "email_address": "user@example.com",
  "reminder_defaults": {
    "enabled": true,
    "minutes_before": [15, 1440]  // 15 minutes, 1 day
  }
}
```

---

## Database Schema

### SQL Schema (Extensions)

```sql
-- ============================================
-- NEW TABLES
-- ============================================

-- Tags table
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) DEFAULT '#6B7280',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_user_tag_name UNIQUE (user_id, name)
);

-- Task-Tag join table (many-to-many)
CREATE TABLE task_tags (
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (task_id, tag_id)
);

-- Reminders table
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    timing_minutes INTEGER DEFAULT 0,
    timing_days INTEGER,
    delivery_channel VARCHAR(20) NOT NULL DEFAULT 'in_app',
    scheduled_time TIMESTAMP NOT NULL,
    sent_at TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_reminder_timing CHECK (
        timing_minutes >= 0 OR timing_days IS NULL OR timing_days >= 0
    ),
    CONSTRAINT chk_delivery_channel CHECK (
        delivery_channel IN ('in_app', 'email', 'web_push', 'sms')
    ),
    CONSTRAINT chk_reminder_status CHECK (
        status IN ('pending', 'sent', 'failed', 'cancelled')
    )
);

-- Recurring tasks table
CREATE TABLE recurring_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    series_id UUID,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    recurrence_pattern VARCHAR(50) NOT NULL,
    interval INTEGER NOT NULL DEFAULT 1,
    by_weekday VARCHAR(50),
    by_monthday INTEGER,
    by_month VARCHAR(50),
    end_condition VARCHAR(20) NOT NULL DEFAULT 'never',
    end_occurrences INTEGER,
    end_date TIMESTAMP,
    last_generated_date TIMESTAMP,
    next_due_date TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_recurrence_pattern CHECK (
        recurrence_pattern IN ('daily', 'weekly', 'monthly', 'yearly', 'custom')
    ),
    CONSTRAINT chk_interval CHECK (interval >= 1),
    CONSTRAINT chk_end_condition CHECK (
        end_condition IN ('never', 'after_occurrences', 'on_date')
    ),
    CONSTRAINT chk_by_monthday CHECK (
        by_monthday IS NULL OR (by_monthday >= 1 AND by_monthday <= 31)
    )
);

-- Domain events table
CREATE TABLE domain_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    aggregate_id UUID NOT NULL,
    aggregate_type VARCHAR(50) NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    payload JSON NOT NULL,
    metadata JSON,
    published BOOLEAN NOT NULL DEFAULT FALSE,
    published_at TIMESTAMP,
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    processed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_event_type CHECK (
        event_type IN (
            'task.created', 'task.updated', 'task.completed', 'task.deleted',
            'task.reminder_sent', 'recurring.instance_generated'
        )
    )
);

-- ============================================
-- EXTENSIONS TO EXISTING TABLES
-- ============================================

-- Add new columns to tasks table
ALTER TABLE tasks
    ADD COLUMN priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    ADD COLUMN due_date TIMESTAMP,
    ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC',
    ADD COLUMN is_recurring BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN recurring_task_id UUID REFERENCES recurring_tasks(id),
    ADD CONSTRAINT chk_priority CHECK (
        priority IN ('low', 'medium', 'high', 'urgent')
    );

-- Add new columns to users table
ALTER TABLE users
    ADD COLUMN timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    ADD COLUMN notification_preferences JSON,
    ADD COLUMN default_task_priority VARCHAR(20) DEFAULT 'medium',
    ADD CONSTRAINT chk_default_priority CHECK (
        default_task_priority IN ('low', 'medium', 'high', 'urgent')
    );

-- ============================================
-- NEW INDEXES
-- ============================================

-- Tags indexes
CREATE INDEX idx_tags_user_id ON tags(user_id);
CREATE INDEX idx_tags_name ON tags(name);

-- Task tags indexes
CREATE INDEX idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag_id ON task_tags(tag_id);

-- Reminders indexes
CREATE INDEX idx_reminders_task_id ON reminders(task_id);
CREATE INDEX idx_reminders_scheduled_time ON reminders(scheduled_time);
CREATE INDEX idx_reminders_status ON reminders(status);
CREATE INDEX idx_reminders_pending ON reminders(status, scheduled_time) 
    WHERE status = 'pending';

-- Recurring tasks indexes
CREATE INDEX idx_recurring_tasks_series_id ON recurring_tasks(series_id);
CREATE INDEX idx_recurring_tasks_task_id ON recurring_tasks(task_id);
CREATE INDEX idx_recurring_tasks_active ON recurring_tasks(is_active) 
    WHERE is_active = TRUE;
CREATE INDEX idx_recurring_tasks_next_due ON recurring_tasks(next_due_date) 
    WHERE is_active = TRUE;

-- Domain events indexes
CREATE INDEX idx_domain_events_type ON domain_events(event_type);
CREATE INDEX idx_domain_events_aggregate ON domain_events(aggregate_id, aggregate_type);
CREATE INDEX idx_domain_events_user_id ON domain_events(user_id);
CREATE INDEX idx_domain_events_published ON domain_events(published, created_at) 
    WHERE published = FALSE;
CREATE INDEX idx_domain_events_processed ON domain_events(processed, created_at) 
    WHERE processed = FALSE;

-- Task indexes (new)
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_is_recurring ON tasks(is_recurring);
CREATE INDEX idx_tasks_recurring_id ON tasks(recurring_task_id);
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_user_due_date ON tasks(user_id, due_date);
CREATE INDEX idx_tasks_user_status_priority ON tasks(user_id, is_completed, priority);
CREATE INDEX idx_tasks_user_status_due_date ON tasks(user_id, is_completed, due_date);

-- ============================================
-- GENERATED COLUMN FOR SEARCH (PostgreSQL FTS)
-- ============================================

-- Add search vector column to tasks
ALTER TABLE tasks
    ADD COLUMN search_vector tsvector
    GENERATED ALWAYS AS (
        to_tsvector('english', 
            coalesce(title, '') || ' ' || 
            coalesce(description, '') || ' ' ||
            coalesce(priority, '')
        )
    ) STORED;

-- Create GIN index for full-text search
CREATE INDEX idx_tasks_search_vector ON tasks USING GIN (search_vector);

-- ============================================
-- DAPR STATE TABLE (for Dapr state management)
-- ============================================

CREATE TABLE IF NOT EXISTS dapr_state (
    key TEXT NOT NULL,
    value JSONB NOT NULL,
    version BIGINT,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (key)
);
```

---

## Indexes Summary

### Performance-Critical Indexes

| Index Name | Table | Columns | Purpose |
|------------|-------|---------|---------|
| idx_tasks_user_priority | tasks | (user_id, priority) | Filter tasks by user and priority |
| idx_tasks_user_due_date | tasks | (user_id, due_date) | Filter tasks by user and due date |
| idx_tasks_user_status_priority | tasks | (user_id, is_completed, priority) | Complex filter + sort |
| idx_reminders_pending | reminders | (status, scheduled_time) | Find pending reminders (partial index) |
| idx_recurring_tasks_next_due | recurring_tasks | (next_due_date) | Find recurring tasks due for generation (partial index) |
| idx_domain_events_published | domain_events | (published, created_at) | Find unpublished events (partial index) |
| idx_tasks_search_vector | tasks | (search_vector) | Full-text search (GIN index) |

---

## State Transitions

### Reminder State Transitions

```
pending → sent (reminder delivered successfully)
pending → failed (delivery failed, will retry)
pending → cancelled (task completed/deleted before delivery)
failed → pending (retry scheduled)
failed → cancelled (max retries exceeded)
```

### Domain Event State Transitions

```
created → published (event sent to Kafka)
published → processed (consumer processed event)
created → processed (direct processing, no Kafka)
published → failed (consumer failed, will retry)
```

### Recurring Task State Transitions

```
active → active (instance generated)
active → inactive (end condition reached)
active → inactive (user manually stopped)
inactive → active (user reactivated)
```

---

## Data Access Patterns

### Common Queries (Extended)

1. **Get tasks with filters and sorting**
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

2. **Search tasks with full-text search**
   ```sql
   SELECT *, ts_rank(search_vector, query) AS rank
   FROM tasks, plainto_tsquery('english', :search_query) query
   WHERE user_id = :user_id
     AND search_vector @@ query
   ORDER BY rank DESC
   LIMIT 50;
   ```

3. **Get pending reminders due now**
   ```sql
   SELECT * FROM reminders
   WHERE status = 'pending'
     AND scheduled_time <= NOW()
   ORDER BY scheduled_time ASC
   LIMIT 100;
   ```

4. **Get recurring tasks due for instance generation**
   ```sql
   SELECT * FROM recurring_tasks
   WHERE is_active = TRUE
     AND (next_due_date IS NULL OR next_due_date <= NOW())
   ORDER BY next_due_date ASC;
   ```

5. **Get unpublished events**
   ```sql
   SELECT * FROM domain_events
   WHERE published = FALSE
   ORDER BY created_at ASC
   LIMIT 100;
   ```

6. **Get user's most-used tags**
   ```sql
   SELECT t.*, COUNT(tt.task_id) AS usage_count
   FROM tags t
   LEFT JOIN task_tags tt ON t.id = tt.tag_id
   WHERE t.user_id = :user_id
   GROUP BY t.id
   ORDER BY usage_count DESC
   LIMIT 10;
   ```

---

## Security Considerations

### User Isolation (Maintained from Phase II)

- All queries MUST filter by user_id
- Foreign key constraints ensure referential integrity
- Users cannot access tasks, tags, reminders, or recurring tasks belonging to other users
- Domain events include user_id for audit trail

### Cascade Deletes

- Deleting a user cascades to: tasks, tags, reminders, recurring_tasks, domain_events
- Deleting a task cascades to: task_tags, reminders
- Deleting a tag cascades to: task_tags
- Deleting a recurring task cascades to: generated task instances

---

## Migration Strategy

### Phase 1: Add New Tables
1. Create tags, task_tags, reminders, recurring_tasks, domain_events tables
2. Create all new indexes

### Phase 2: Extend Existing Tables
1. Add new columns to tasks (priority, due_date, timezone, is_recurring, recurring_task_id)
2. Add new columns to users (timezone, notification_preferences, default_task_priority)
3. Add search_vector column and GIN index

### Phase 3: Data Migration
1. Set default priority for existing tasks ('medium')
2. Set default timezone for existing users ('UTC')
3. Backfill search_vector for existing tasks

### Phase 4: Dapr Setup
1. Create dapr_state table
2. Configure Dapr components
3. Test state management operations

---

## Next Steps

1. **Create API Contracts**: Define OpenAPI specs for new endpoints
2. **Write Migrations**: Create SQLModel migration scripts
3. **Update Models**: Extend SQLModel classes with new entities
4. **Implement Services**: Create service classes for new features
