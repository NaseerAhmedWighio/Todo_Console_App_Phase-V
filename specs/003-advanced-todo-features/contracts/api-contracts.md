# API Contracts: Advanced Todo Features - Phase III

**Feature**: 003-advanced-todo-features  
**Date**: 2026-02-19  
**Format**: OpenAPI 3.0

---

## Overview

This document defines the API contracts for advanced todo features including recurring tasks, reminders, priorities, tags, search, filtering, and sorting. All endpoints require JWT authentication.

**Base URL**: `/api/v1`  
**Authentication**: Bearer Token (JWT from Better Auth)

---

## New Endpoints

### 1. Tags API

#### GET /tags
List all tags for the authenticated user.

**Request**:
```http
GET /api/v1/tags HTTP/1.1
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "work",
      "color": "#3B82F6",
      "usage_count": 5,
      "created_at": "2026-02-19T10:00:00Z"
    }
  ]
}
```

**Query Parameters**:
- `limit` (integer, optional): Max results (default: 100)
- `offset` (integer, optional): Pagination offset

---

#### POST /tags
Create a new tag.

**Request**:
```http
POST /api/v1/tags HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "urgent",
  "color": "#EF4444"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "urgent",
    "color": "#EF4444",
    "created_at": "2026-02-19T10:00:00Z"
  }
}
```

**Validation Rules**:
- name: required, 1-50 characters, alphanumeric + spaces
- color: optional, valid hex format (#RRGGBB), default: #6B7280

**Error Responses**:
- 400 Bad Request: Invalid name or color format
- 409 Conflict: Tag with same name already exists

---

#### PUT /tags/{tag_id}
Update a tag.

**Request**:
```http
PUT /api/v1/tags/{tag_id} HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "high-priority",
  "color": "#F59E0B"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "high-priority",
    "color": "#F59E0B",
    "updated_at": "2026-02-19T10:00:00Z"
  }
}
```

---

#### DELETE /tags/{tag_id}
Delete a tag (removes from all tasks).

**Response** (204 No Content):
```json
{
  "success": true,
  "message": "Tag deleted successfully"
}
```

---

#### POST /tags/{tag_id}/assign
Assign a tag to a task.

**Request**:
```http
POST /api/v1/tags/{tag_id}/assign HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "task_id": "uuid"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Tag assigned to task"
}
```

**Error Responses**:
- 404 Not Found: Tag or task not found
- 403 Forbidden: Task doesn't belong to user

---

#### DELETE /tags/{tag_id}/unassign
Remove a tag from a task.

**Request**:
```http
DELETE /api/v1/tags/{tag_id}/unassign?task_id={task_id} HTTP/1.1
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Tag removed from task"
}
```

---

### 2. Search API

#### GET /search
Search tasks with full-text search and filters.

**Request**:
```http
GET /api/v1/search?q=groceries&priority=high&status=pending&limit=20 HTTP/1.1
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "uuid",
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "priority": "high",
        "is_completed": false,
        "due_date": "2026-02-20T18:00:00Z",
        "tags": [{"id": "uuid", "name": "shopping", "color": "#10B981"}],
        "relevance_score": 0.95
      }
    ],
    "total": 1,
    "query": "groceries",
    "filters": {
      "priority": "high",
      "status": "pending"
    }
  }
}
```

**Query Parameters**:
- `q` (string, required): Search query
- `priority` (string, optional): Filter by priority (low, medium, high, urgent)
- `status` (string, optional): Filter by status (pending, completed)
- `tag_id` (string, optional): Filter by tag
- `due_date_from` (string, optional): Filter by due date (ISO 8601)
- `due_date_to` (string, optional): Filter by due date (ISO 8601)
- `limit` (integer, optional): Max results (default: 50)
- `offset` (integer, optional): Pagination offset

---

### 3. Reminders API

#### GET /reminders
List all reminders for the authenticated user.

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "task_id": "uuid",
      "task_title": "Submit report",
      "timing_minutes": 30,
      "timing_days": null,
      "delivery_channel": "email",
      "scheduled_time": "2026-02-20T17:30:00Z",
      "status": "pending",
      "created_at": "2026-02-19T10:00:00Z"
    }
  ]
}
```

---

#### POST /reminders
Create a new reminder for a task.

**Request**:
```http
POST /api/v1/reminders HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "task_id": "uuid",
  "timing_minutes": 30,
  "timing_days": null,
  "delivery_channel": "email"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "task_id": "uuid",
    "scheduled_time": "2026-02-20T17:30:00Z",
    "status": "pending",
    "created_at": "2026-02-19T10:00:00Z"
  }
}
```

**Validation Rules**:
- task_id: required, must exist and belong to user
- task must have a due_date
- Either timing_minutes or timing_days must be provided
- delivery_channel: one of 'in_app', 'email', 'web_push', 'sms'

**Error Responses**:
- 400 Bad Request: Invalid timing or task has no due date
- 404 Not Found: Task not found

---

#### DELETE /reminders/{reminder_id}
Delete a reminder.

**Response** (204 No Content):
```json
{
  "success": true,
  "message": "Reminder deleted successfully"
}
```

---

### 4. Recurring Tasks API

#### POST /todos/{todo_id}/recurring
Configure a task as recurring.

**Request**:
```http
POST /api/v1/todos/{todo_id}/recurring HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "recurrence_pattern": "weekly",
  "interval": 1,
  "by_weekday": "0,2,4",
  "by_monthday": null,
  "by_month": null,
  "end_condition": "never",
  "end_occurrences": null,
  "end_date": null
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "task_id": "uuid",
    "recurrence_pattern": "weekly",
    "interval": 1,
    "by_weekday": "0,2,4",
    "next_due_date": "2026-02-23T09:00:00Z",
    "is_active": true,
    "created_at": "2026-02-19T10:00:00Z"
  }
}
```

**Validation Rules**:
- recurrence_pattern: required, one of 'daily', 'weekly', 'monthly', 'yearly', 'custom'
- interval: required, >= 1
- by_weekday: required for weekly pattern (comma-separated 0-6)
- by_monthday: required for monthly pattern (1-31)
- by_month: required for yearly pattern (comma-separated 1-12)
- end_occurrences: required if end_condition = 'after_occurrences'
- end_date: required if end_condition = 'on_date'

**Error Responses**:
- 400 Bad Request: Invalid recurrence configuration
- 404 Not Found: Task not found

---

#### GET /todos/{todo_id}/recurring
Get recurring configuration for a task.

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "recurrence_pattern": "weekly",
    "interval": 1,
    "by_weekday": "0,2,4",
    "end_condition": "never",
    "next_due_date": "2026-02-23T09:00:00Z",
    "is_active": true
  }
}
```

---

#### PUT /todos/{todo_id}/recurring
Update recurring configuration.

**Request**: Same as POST

**Response** (200 OK): Updated recurring configuration

---

#### DELETE /todos/{todo_id}/recurring
Remove recurring configuration from a task.

**Query Parameters**:
- `delete_all_instances` (boolean, optional): 
  - true: Delete all generated instances
  - false: Keep existing instances (default)

**Response** (204 No Content):
```json
{
  "success": true,
  "message": "Recurring configuration removed"
}
```

---

#### GET /recurring-tasks
List all recurring tasks for the user.

**Query Parameters**:
- `is_active` (boolean, optional): Filter by active status

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "task": {
        "id": "uuid",
        "title": "Team meeting",
        "description": "Weekly sync"
      },
      "recurrence_pattern": "weekly",
      "interval": 1,
      "by_weekday": "1",
      "next_due_date": "2026-02-20T10:00:00Z",
      "is_active": true
    }
  ]
}
```

---

## Extended Endpoints

### 5. Tasks API (Extended)

#### POST /todos (Extended)
Create a new task with advanced fields.

**Request** (Extended):
```http
POST /api/v1/todos HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Submit quarterly report",
  "description": "Complete Q1 financial report",
  "priority": "high",
  "due_date": "2026-03-31T17:00:00Z",
  "tags": ["uuid1", "uuid2"],
  "reminders": [
    {"timing_minutes": 1440, "delivery_channel": "email"}
  ]
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Submit quarterly report",
    "description": "Complete Q1 financial report",
    "priority": "high",
    "is_completed": false,
    "due_date": "2026-03-31T17:00:00Z",
    "tags": [
      {"id": "uuid1", "name": "work", "color": "#3B82F6"},
      {"id": "uuid2", "name": "finance", "color": "#10B981"}
    ],
    "reminders": [
      {
        "id": "uuid",
        "timing_minutes": 1440,
        "scheduled_time": "2026-03-30T17:00:00Z",
        "status": "pending"
      }
    ],
    "created_at": "2026-02-19T10:00:00Z",
    "updated_at": "2026-02-19T10:00:00Z"
  }
}
```

**New Fields**:
- priority: optional, one of 'low', 'medium', 'high', 'urgent' (default: 'medium')
- due_date: optional, ISO 8601 datetime
- tags: optional, array of tag IDs
- reminders: optional, array of reminder configurations

---

#### PUT /todos/{todo_id} (Extended)
Update a task with advanced fields.

**Request** (Extended):
```http
PUT /api/v1/todos/{todo_id} HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated title",
  "priority": "urgent",
  "due_date": "2026-03-30T17:00:00Z",
  "tags": ["uuid1", "uuid3"],
  "reminders": [
    {"id": "existing_id", "timing_minutes": 60},
    {"timing_minutes": 1440, "delivery_channel": "email"}
  ]
}
```

**Response** (200 OK): Updated task with all fields

**Notes**:
- Tags array replaces existing tags (use tag assign/unassign endpoints for incremental updates)
- Reminders array: existing reminders by ID are updated, new ones are created, omitted ones are deleted

---

#### GET /todos (Extended)
List tasks with filters and sorting.

**Request** (Extended):
```http
GET /api/v1/todos?priority=high&status=pending&tag_id=uuid&sort_by=due_date&sort_order=asc&limit=20 HTTP/1.1
Authorization: Bearer <token>
```

**Query Parameters** (New):
- `priority` (string, optional): Filter by priority
- `tag_id` (string, optional): Filter by tag
- `due_date_from` (string, optional): Filter by due date range (start)
- `due_date_to` (string, optional): Filter by due date range (end)
- `sort_by` (string, optional): Sort field
  - 'due_date' (default)
  - 'priority'
  - 'created_at'
  - 'updated_at'
  - 'title'
  - 'completed_at'
- `sort_order` (string, optional): Sort order
  - 'asc' (ascending)
  - 'desc' (descending, default for due_date)
- `limit` (integer, optional): Max results (default: 100)
- `offset` (integer, optional): Pagination offset

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "title": "Urgent task",
      "priority": "high",
      "due_date": "2026-02-20T18:00:00Z",
      "tags": [...],
      ...
    }
  ],
  "pagination": {
    "total": 50,
    "limit": 20,
    "offset": 0,
    "has_more": true
  },
  "filters": {
    "priority": "high",
    "status": "pending",
    "tag_id": "uuid"
  },
  "sort": {
    "by": "due_date",
    "order": "asc"
  }
}
```

---

#### GET /todos/{todo_id} (Extended)
Get a specific task with all details.

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Task title",
    "description": "Task description",
    "priority": "high",
    "is_completed": false,
    "due_date": "2026-02-20T18:00:00Z",
    "timezone": "America/New_York",
    "tags": [
      {"id": "uuid", "name": "work", "color": "#3B82F6"}
    ],
    "reminders": [
      {
        "id": "uuid",
        "timing_minutes": 30,
        "scheduled_time": "2026-02-20T17:30:00Z",
        "status": "pending",
        "delivery_channel": "email"
      }
    ],
    "recurring_info": {
      "is_recurring": true,
      "recurrence_pattern": "weekly",
      "next_due_date": "2026-02-27T18:00:00Z"
    },
    "created_at": "2026-02-19T10:00:00Z",
    "updated_at": "2026-02-19T10:00:00Z"
  }
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "reason"
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| UNAUTHORIZED | 401 | Missing or invalid JWT token |
| FORBIDDEN | 403 | User doesn't have access to this resource |
| NOT_FOUND | 404 | Resource not found |
| VALIDATION_ERROR | 400 | Request validation failed |
| CONFLICT | 409 | Resource conflict (e.g., duplicate tag name) |
| INTERNAL_ERROR | 500 | Internal server error |

---

## Rate Limiting

All endpoints are subject to rate limiting:

- **Standard endpoints**: 100 requests per minute per user
- **Search endpoint**: 30 requests per minute per user
- **Event publishing**: 200 requests per minute per user

**Rate Limit Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1645267200
```

**429 Too Many Requests Response**:
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "retry_after": 60
  }
}
```

---

## WebSocket Events (Extended)

The existing WebSocket endpoint now emits additional event types:

### Event Types

```json
{
  "type": "task.created",
  "payload": {
    "task_id": "uuid",
    "task": {...}
  }
}
```

```json
{
  "type": "task.updated",
  "payload": {
    "task_id": "uuid",
    "changes": {...}
  }
}
```

```json
{
  "type": "reminder.sent",
  "payload": {
    "reminder_id": "uuid",
    "task_id": "uuid",
    "delivery_channel": "email"
  }
}
```

```json
{
  "type": "recurring.instance_created",
  "payload": {
    "recurring_task_id": "uuid",
    "new_task_id": "uuid",
    "due_date": "2026-02-23T09:00:00Z"
  }
}
```

---

## Next Steps

1. **Implement Endpoints**: Create FastAPI route handlers for all new endpoints
2. **Add Validation**: Implement Pydantic models for request/response validation
3. **Update OpenAPI Spec**: Generate complete OpenAPI 3.0 specification
4. **Write Integration Tests**: Test all endpoints with various scenarios
5. **Update Frontend**: Integrate new endpoints into React components
