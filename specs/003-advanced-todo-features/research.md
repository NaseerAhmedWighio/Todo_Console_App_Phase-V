# Research & Discovery: Advanced Todo Features - Phase III

**Feature**: 003-advanced-todo-features  
**Date**: 2026-02-19  
**Spec**: [spec.md](spec.md)

---

## Research Task 1: Kafka Integration with FastAPI

### Decision
Use **kafka-python** library with synchronous KafkaProducer/KafkaConsumer, wrapped in async-compatible service layer for FastAPI integration.

### Rationale
- **Maturity**: kafka-python is the most mature Python Kafka client (actively maintained since 2014)
- **Simplicity**: Straightforward API, well-documented, large community
- **FastAPI Integration**: Can be wrapped in async service layer using asyncio.to_thread() for non-blocking operations
- **Error Handling**: Built-in retry mechanisms, connection pooling, automatic reconnection
- **Performance**: Sufficient for our scale (10k tasks, 100ms p95 latency requirement)

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **aiokafka** | Async-native, better performance with asyncio | Less mature, smaller community, fewer examples | Added complexity not needed for our scale |
| **confluent-kafka** | Fastest performance (C library), official Confluent support | Requires librdkafka C library installation, more complex setup | Installation complexity outweighs performance benefits |
| **Direct HTTP to Kafka REST Proxy** | No Python dependencies, language-agnostic | Additional infrastructure (REST Proxy), higher latency | Extra infrastructure not justified |

### Implementation Pattern

```python
# backend/app/events/publisher.py
from kafka import KafkaProducer
import json
from typing import Dict, Any

class EventPublisher:
    def __init__(self, bootstrap_servers: list):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',  # Wait for all replicas to acknowledge
            retries=3,
            retry_backoff_ms=100
        )
    
    async def publish(self, topic: str, event_type: str, payload: Dict[str, Any], user_id: str):
        """Publish event to Kafka topic"""
        message = {
            'event_type': event_type,
            'payload': payload,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Use asyncio.to_thread() for non-blocking send
        await asyncio.to_thread(
            self.producer.send,
            topic,
            key=user_id,
            value=message
        )
```

### Best Practices Identified

1. **Event Schema Versioning**: Include schema_version in all events for backward compatibility
2. **Idempotent Producers**: Enable idempotence to prevent duplicate events on retries
3. **Topic Naming**: Use hierarchical naming (e.g., `todo.tasks.created`, `todo.tasks.updated`)
4. **Error Handling**: Implement dead letter queue for failed messages
5. **Monitoring**: Track producer metrics (latency, error rates, queue size)

---

## Research Task 2: Dapr State Management for Python

### Decision
Use **Dapr Python SDK** with PostgreSQL state store component for persistent state management.

### Rationale
- **Official Support**: Dapr Python SDK is officially maintained by Microsoft
- **Simplicity**: Clean API for state operations (save, get, delete, transaction)
- **Sidecar Pattern**: Dapr sidecar handles all complexity (state store connections, retries, consistency)
- **Multi-Component Support**: Same API works with different state stores (PostgreSQL, Redis, etc.)
- **Pub/Sub Integration**: Unified SDK for both state management and pub/sub messaging

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Direct HTTP to Dapr API** | No SDK dependencies, full control | Verbose, error-prone, manual serialization | SDK provides better developer experience |
| **Direct PostgreSQL (no Dapr)** | Simpler architecture, no sidecar | Loses distributed runtime benefits, manual scaling | Violates constitutional principle of distributed runtime |
| **Redis for state** | Faster, simpler | Less durable than PostgreSQL, additional infrastructure | PostgreSQL already in use, durability critical |

### Implementation Pattern

```python
# backend/app/dapr/state.py
from dapr.clients import DaprClient
from typing import Dict, Any, Optional

class DaprStateManager:
    def __init__(self, state_store_name: str = "todo-statestore"):
        self.state_store_name = state_store_name
    
    async def save_state(self, key: str, value: Dict[str, Any]) -> bool:
        """Save state to Dapr state store"""
        with DaprClient() as client:
            await client.save_state(
                store_name=self.state_store_name,
                key=key,
                value=json.dumps(value)
            )
            return True
    
    async def get_state(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve state from Dapr state store"""
        with DaprClient() as client:
            response = await client.get_state(
                store_name=self.state_store_name,
                key=key
            )
            return json.loads(response.data) if response.data else None
    
    async def delete_state(self, key: str) -> bool:
        """Delete state from Dapr state store"""
        with DaprClient() as client:
            await client.delete_state(
                store_name=self.state_store_name,
                key=key
            )
            return True
```

### Dapr Component Configuration

```yaml
# dapr/components/statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "postgresql://user:pass@host:5432/neondb?sslmode=require"
  - name: tableName
    value: dapr_state
```

### Best Practices Identified

1. **State Store Selection**: Use PostgreSQL for durability (already in stack)
2. **Key Naming**: Use hierarchical keys (e.g., `user:{id}:settings`, `task:{id}:metadata`)
3. **Transaction Support**: Use Dapr transactions for multi-key operations
4. **ETag for Concurrency**: Use ETag for optimistic concurrency control
5. **State Cleanup**: Implement TTL for temporary state to prevent bloat

---

## Research Task 3: Recurring Task Date Calculation

### Decision
Implement **custom recurrence engine** inspired by RFC 5545 (iCalendar) but simplified for our specific use cases.

### Rationale
- **Control**: Full control over edge case handling (month-end dates, leap years, timezone changes)
- **Simplicity**: Only implement needed recurrence patterns (daily, weekly, monthly, yearly, custom)
- **Performance**: Optimized for our specific queries (next occurrence, generate instances)
- **Timezone Awareness**: Built-in timezone handling using pytz or zoneinfo

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **python-dateutil.rrule** | Full RFC 5545 implementation, battle-tested | Complex API, overkill for our needs, timezone handling tricky | More complexity than needed |
| **recurrence library** | Lightweight, simpler API | Less feature-complete, smaller community | Limited documentation and examples |
| **Full iCalendar library** | Complete standard implementation | Very complex, large dependency, performance overhead | Unnecessary for our limited recurrence patterns |

### Recurrence Pattern Data Structure

```python
from enum import Enum
from typing import Optional, List
from datetime import datetime, timedelta

class RecurrenceFrequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"  # e.g., every 2 weeks, every 3rd Monday

class RecurrencePattern:
    def __init__(
        self,
        frequency: RecurrenceFrequency,
        interval: int = 1,  # every N units
        by_weekday: Optional[List[int]] = None,  # 0=Monday, 6=Sunday
        by_monthday: Optional[int] = None,  # 1-31
        by_month: Optional[List[int]] = None,  # 1-12
        count: Optional[int] = None,  # end after N occurrences
        until: Optional[datetime] = None  # end on specific date
    ):
        self.frequency = frequency
        self.interval = interval
        self.by_weekday = by_weekday
        self.by_monthday = by_monthday
        self.by_month = by_month
        self.count = count
        self.until = until
    
    def get_next_occurrence(self, from_date: datetime, timezone: str) -> datetime:
        """Calculate next occurrence from given date"""
        # Implementation handles:
        # - Month-end edge cases (31st → 28th/29th/30th)
        # - Leap years
        # - Timezone changes (DST)
        # - Skipped dates
        pass
    
    def generate_instances(
        self,
        start_date: datetime,
        end_date: datetime,
        timezone: str
    ) -> List[datetime]:
        """Generate all occurrences between two dates"""
        # Efficiently generate instances for bulk operations
        pass
```

### Edge Case Handling

1. **Month-End Dates**: 
   - If pattern is "31st of month" and month has 30 days → use 30th
   - If pattern is "31st of month" and February → use 28th/29th
   - Configurable: "skip invalid dates" vs "use last day of month"

2. **Leap Years**:
   - If pattern is "Feb 29" and non-leap year → use Feb 28 or skip year
   - Configurable behavior

3. **Timezone Changes (DST)**:
   - Store all dates in UTC with user's timezone preference
   - When calculating occurrences, convert to user timezone first
   - Handle "2 AM doesn't exist" and "2 AM happens twice" scenarios

4. **Custom Patterns**:
   - "Every 2 weeks on Monday and Wednesday"
   - "Every 3rd Monday of the month"
   - "First weekday of each month"

### Best Practices Identified

1. **Store Original Pattern**: Always store the original recurrence pattern, not just generated instances
2. **Lazy Generation**: Generate instances on-demand (next 30-90 days) rather than all at once
3. **Series Identification**: Use series_id to link all instances of a recurring task
4. **Instance Override**: Allow individual instances to be modified without affecting series
5. **Cleanup**: Implement cleanup for old completed instances to prevent database bloat

---

## Research Task 4: Reminder Delivery Systems

### Decision
Implement **multi-channel reminder delivery** with in-app notifications (primary) and email (secondary), using background workers for scheduled processing.

### Rationale
- **User Choice**: Users can choose preferred notification channel
- **Reliability**: Multiple channels increase delivery success rate
- **Progressive Enhancement**: Start with in-app (simplest), add email later
- **Background Processing**: Decouple reminder scheduling from delivery

### Notification Channel Comparison

| Channel | Pros | Cons | Implementation Complexity |
|---------|------|------|---------------------------|
| **In-App Notifications** | Instant, no external dependencies, full control | Only works when user is active | Low |
| **Email** | Works offline, familiar, reliable | Requires email service, deliverability concerns | Medium |
| **Web Push** | Works when browser closed, instant | Requires service worker, browser support | Medium-High |
| **SMS** | Highest open rate, instant | Cost per message, privacy concerns | High |

### Implementation Architecture

```python
# backend/app/services/reminder_service.py
from enum import Enum
from typing import List, Optional
from datetime import datetime, timedelta

class NotificationChannel(Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    WEB_PUSH = "web_push"
    SMS = "sms"

class ReminderDelivery:
    def __init__(self):
        self.notification_queue = []  # Backed by database for persistence
    
    async def schedule_reminder(
        self,
        task_id: str,
        user_id: str,
        due_date: datetime,
        reminders: List[dict],  # [{channel, minutes_before}, ...]
        user_timezone: str
    ):
        """Schedule reminders for a task"""
        for reminder in reminders:
            delivery_time = due_date - timedelta(minutes=reminder['minutes_before'])
            
            # Convert to user timezone for scheduling
            delivery_time_local = delivery_time.astimezone(
                ZoneInfo(user_timezone)
            )
            
            # Create reminder record in database
            await self._create_reminder_record(
                task_id=task_id,
                user_id=user_id,
                channel=reminder['channel'],
                scheduled_time=delivery_time_local
            )
    
    async def process_due_reminders(self):
        """Background worker: process reminders that are due now"""
        due_reminders = await self._get_due_reminders()
        
        for reminder in due_reminders:
            try:
                if reminder.channel == NotificationChannel.IN_APP:
                    await self._send_in_app_notification(reminder)
                elif reminder.channel == NotificationChannel.EMAIL:
                    await self._send_email_notification(reminder)
                elif reminder.channel == NotificationChannel.WEB_PUSH:
                    await self._send_web_push_notification(reminder)
                
                # Mark as sent
                await self._mark_reminder_sent(reminder.id)
                
            except Exception as e:
                # Log error, retry later
                await self._handle_delivery_failure(reminder, e)
```

### Email Service Options

| Service | Cost | Deliverability | Ease of Integration |
|---------|------|----------------|---------------------|
| **SendGrid** | Free 100/day, then $15/million | Excellent | Easy (REST API, Python SDK) |
| **AWS SES** | $0.10/million | Excellent | Medium (AWS SDK) |
| **Postmark** | $15/million | Best | Easy (REST API) |
| **SMTP (self-hosted)** | Free | Poor (spam issues) | Hard (maintain reputation) |

**Recommendation**: Start with SendGrid free tier, migrate to AWS SES at scale

### Retry Strategy for Failed Deliveries

1. **Immediate Retry**: Retry once immediately for transient errors (network timeout)
2. **Exponential Backoff**: Retry at 1min, 5min, 15min, 1hr intervals
3. **Max Retries**: Give up after 3-5 attempts
4. **Dead Letter Queue**: Store failed reminders for manual review
5. **User Notification**: Notify user of persistent delivery failures

### Best Practices Identified

1. **Idempotency**: Use reminder_id to prevent duplicate deliveries
2. **Timezone Handling**: Always store and calculate in user's timezone
3. **Cancellation**: Immediately cancel reminders when task is completed/deleted
4. **Rate Limiting**: Respect email service rate limits to avoid throttling
5. **Unsubscribe**: Provide easy opt-out for email reminders
6. **Delivery Tracking**: Track delivery status, open rates for analytics

---

## Research Task 5: PostgreSQL Full-Text Search

### Decision
Use **PostgreSQL native full-text search** with tsvector indexes for task search functionality.

### Rationale
- **No Additional Infrastructure**: Uses existing PostgreSQL database (Neon)
- **Performance**: tsvector indexes provide fast search even for large datasets
- **Relevance Ranking**: Built-in ranking functions (ts_rank, ts_rank_cd)
- **Integration**: Works seamlessly with SQLModel ORM
- **Cost**: No additional cost (vs. external search services)

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **Elasticsearch** | Most powerful, advanced features | Additional infrastructure, operational complexity, cost | Overkill for 10k tasks per user |
| **Algolia** | Excellent relevance, typo tolerance, analytics | External dependency, cost ($0.50/1k searches), latency | Cost adds up, unnecessary for our scale |
| **Meilisearch** | Fast, typo-tolerant, open-source | Additional service to maintain, learning curve | PostgreSQL FTS sufficient for our needs |
| **SQL LIKE queries** | Simple, no setup | Very slow, no relevance ranking, no fuzzy matching | Doesn't meet performance requirements |

### Implementation Pattern

```python
# backend/app/services/search_service.py
from sqlmodel import SQLModel, Session, select, func, text
from typing import List, Optional

class SearchService:
    async def search_tasks(
        self,
        user_id: str,
        query: str,
        filters: Optional[dict] = None,
        limit: int = 50
    ) -> List[Task]:
        """Search tasks with full-text search"""
        
        # Create tsquery from search string
        # Convert "word1 word2" to "word1 & word2" for AND search
        search_query = " & ".join(query.split())
        
        # Build search statement
        statement = select(Task).where(
            Task.user_id == user_id,
            # Match against tsvector
            func.to_tsvector('english', Task.title + ' ' + Task.description).op('@@')(
                func.plainto_tsquery('english', search_query)
            )
        )
        
        # Add filters (status, priority, tags, date range)
        if filters:
            if 'status' in filters:
                statement = statement.where(Task.is_completed == filters['status'])
            if 'priority' in filters:
                statement = statement.where(Task.priority == filters['priority'])
            # ... more filters
        
        # Order by relevance
        statement = statement.order_by(
            func.ts_rank(
                func.to_tsvector('english', Task.title + ' ' + Task.description),
                func.plainto_tsquery('english', search_query)
            ).desc()
        )
        
        statement = statement.limit(limit)
        
        with Session(engine) as session:
            results = session.exec(statement).all()
            return results
    
    async def create_search_index(self):
        """Create GIN index for full-text search (run once in migration)"""
        # CREATE INDEX idx_tasks_search ON tasks 
        # USING GIN (to_tsvector('english', title || ' ' || description));
        pass
```

### Index Optimization Strategies

1. **Generated Column**: Store tsvector in generated column to avoid recomputation
   ```sql
   ALTER TABLE tasks ADD COLUMN search_vector tsvector
   GENERATED ALWAYS AS (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))) STORED;
   
   CREATE INDEX idx_tasks_search ON tasks USING GIN (search_vector);
   ```

2. **Triggers for Auto-Update**: If using older PostgreSQL without generated columns
   ```sql
   CREATE TRIGGER tasks_search_vector_update
   BEFORE UPDATE ON tasks
   FOR EACH ROW EXECUTE FUNCTION
   tsvector_update_trigger(search_vector, 'pg_catalog.english', title, description);
   ```

3. **Multi-Column Search**: Include tags, priority in search vector
   ```sql
   CREATE INDEX idx_tasks_search_all ON tasks USING GIN (
     to_tsvector('english', 
       coalesce(title, '') || ' ' || 
       coalesce(description, '') || ' ' ||
       coalesce(priority, '')
     )
   );
   ```

### Performance Benchmarks (from PostgreSQL documentation)

| Dataset Size | Index Type | Query Time |
|--------------|------------|------------|
| 10k rows | GIN tsvector | ~5-10ms |
| 100k rows | GIN tsvector | ~20-50ms |
| 1M rows | GIN tsvector | ~100-200ms |

**Our Target**: 10k tasks per user → should achieve <100ms search latency easily

### Best Practices Identified

1. **Weighted Search**: Give higher weight to title matches vs description
   ```sql
   setweight(to_tsvector('english', title), 'A') || 
   setweight(to_tsvector('english', description), 'B')
   ```

2. **Prefix Matching**: Support autocomplete with prefix queries
   ```python
   # "buy" matches "buy", "buying", "buyer"
   query = "buy:*"  # Prefix match
   ```

3. **Fuzzy Matching**: Use trigram similarity for typo tolerance
   ```sql
   -- Enable trigram extension
   CREATE EXTENSION pg_trgm;
   
   -- Search with similarity
   SELECT * FROM tasks 
   WHERE similarity(title, 'grocries') > 0.3  -- Fuzzy match "groceries"
   ORDER BY similarity DESC;
   ```

4. **Search Analytics**: Track popular searches, zero-result queries for improvements

---

## Research Task 6: Tag Management System Design

### Decision
Implement **many-to-many tag relationship** with separate Tag and TaskTag tables, user-scoped tags.

### Rationale
- **Flexibility**: Tasks can have multiple tags, tags can be reused across tasks
- **Efficiency**: Normalized schema, efficient queries for filtering by tag
- **User Isolation**: Tags scoped to user (maintains Phase II isolation)
- **Extensibility**: Easy to add tag metadata (color, icon, description)

### Schema Design

```sql
-- Tags table
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) DEFAULT '#6B7280',  -- Hex color code
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, name)  -- Unique tag names per user
);

-- Many-to-many join table
CREATE TABLE task_tags (
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (task_id, tag_id)
);

-- Indexes for efficient queries
CREATE INDEX idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag_id ON task_tags(tag_id);
CREATE INDEX idx_tags_user_id ON tags(user_id);
```

### Tag Operations

```python
# backend/app/services/tag_service.py
from sqlmodel import SQLModel, Session, select

class TagService:
    async def create_tag(self, user_id: str, name: str, color: str = None) -> Tag:
        """Create a new tag for user"""
        # Check for duplicate
        existing = session.exec(
            select(Tag).where(Tag.user_id == user_id, Tag.name == name)
        ).first()
        
        if existing:
            raise ValueError("Tag with this name already exists")
        
        tag = Tag(user_id=user_id, name=name, color=color or '#6B7280')
        session.add(tag)
        session.commit()
        return tag
    
    async def assign_tag_to_task(self, task_id: str, tag_id: str, user_id: str):
        """Assign a tag to a task"""
        # Verify task and tag belong to user
        task = session.get(Task, task_id)
        tag = session.get(Tag, tag_id)
        
        if not task or task.user_id != user_id:
            raise HTTPException(403, "Task not found or access denied")
        if not tag or tag.user_id != user_id:
            raise HTTPException(403, "Tag not found or access denied")
        
        # Check if already assigned
        existing = session.exec(
            select(TaskTag).where(
                TaskTag.task_id == task_id,
                TaskTag.tag_id == tag_id
            )
        ).first()
        
        if existing:
            return  # Already assigned
        
        # Create assignment
        task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
        session.add(task_tag)
        session.commit()
    
    async def get_tasks_by_tag(self, user_id: str, tag_id: str) -> List[Task]:
        """Get all tasks with a specific tag"""
        statement = select(Task).join(TaskTag).where(
            Task.user_id == user_id,
            TaskTag.tag_id == tag_id
        )
        return session.exec(statement).all()
    
    async def delete_tag(self, user_id: str, tag_id: str):
        """Delete a tag (automatically removes from all tasks)"""
        tag = session.get(Tag, tag_id)
        
        if not tag or tag.user_id != user_id:
            raise HTTPException(404, "Tag not found")
        
        # Cascade delete handles task_tags removal
        session.delete(tag)
        session.commit()
```

### Tag Autocomplete Implementation

```python
async def search_tags(self, user_id: str, query: str, limit: int = 10) -> List[Tag]:
    """Search tags for autocomplete"""
    statement = select(Tag).where(
        Tag.user_id == user_id,
        Tag.name.ilike(f"%{query}%")  # Case-insensitive partial match
    ).limit(limit)
    
    return session.exec(statement).all()
```

### Tag Management Features

1. **Tag Merging**: Merge duplicate tags (e.g., "work" and "Work")
   ```python
   async def merge_tags(self, source_tag_id: str, target_tag_id: str, user_id: str):
       """Merge source tag into target tag"""
       # Reassign all task_tags from source to target
       # Delete source tag
       pass
   ```

2. **Tag Suggestions**: Suggest existing tags when creating new ones
   ```python
   async def suggest_tags(self, user_id: str, limit: int = 5) -> List[Tag]:
       """Suggest most-used tags"""
       statement = select(Tag).join(TaskTag).where(
           Tag.user_id == user_id
       ).group_by(Tag.id).order_by(
           func.count(TaskTag.task_id).desc()
       ).limit(limit)
       
       return session.exec(statement).all()
   ```

3. **Unused Tag Cleanup**: Identify tags not used in any task
   ```python
   async def get_unused_tags(self, user_id: str) -> List[Tag]:
       """Get tags not assigned to any task"""
       statement = select(Tag).where(
           Tag.user_id == user_id,
           ~Tag.task_tags.any()  # No associated task_tags
       )
       return session.exec(statement).all()
   ```

### Best Practices Identified

1. **Tag Name Validation**: Enforce length limits (1-50 chars), prevent special characters
2. **Case Normalization**: Store tag names in lowercase for consistent matching
3. **Color Accessibility**: Provide accessible color palette, ensure contrast
4. **Tag Limits**: Consider limiting tags per task (5-10) to prevent abuse
5. **Soft Delete**: Consider soft delete for tags to prevent accidental data loss

---

## Summary of Technology Choices

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Event Streaming** | Apache Kafka + kafka-python | Mature, scalable, supports event retention |
| **Distributed Runtime** | Dapr + Python SDK | Production-ready, handles complexity |
| **State Store** | PostgreSQL (via Dapr) | Durable, already in stack |
| **Recurring Tasks** | Custom engine (RFC 5545 inspired) | Control over edge cases, simpler than full library |
| **Reminders** | In-app + Email (SendGrid) | Multi-channel, progressive enhancement |
| **Background Workers** | Celery + Redis | Mature, scalable, scheduled task support |
| **Search** | PostgreSQL FTS + GIN index | No new infrastructure, good performance |
| **Tags** | Many-to-many SQLModel tables | Standard pattern, efficient queries |

---

## Next Steps

1. **Create Data Model**: Extend existing models with new entities (data-model.md)
2. **Define API Contracts**: Create OpenAPI specs for new endpoints (contracts/)
3. **Write Quick Start**: Document setup and verification steps (quickstart.md)
4. **Update Agent Context**: Add new technologies to constitution agent context
