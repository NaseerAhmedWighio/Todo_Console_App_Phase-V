"""
Event Schemas
Pydantic models for event payloads
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


class EventSchema(BaseModel):
    """Base schema for all domain events"""
    event_type: str = Field(..., description="Type of event")
    payload: Dict[str, Any] = Field(..., description="Event payload data")
    user_id: str = Field(..., description="ID of user who triggered the event")
    aggregate_id: Optional[str] = Field(None, description="ID of the aggregate")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    schema_version: str = Field(default="1.0", description="Event schema version")


# Task event payloads
class TaskCreatedPayload(BaseModel):
    """Payload for task.created event"""
    id: str
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    priority: str = "medium"
    due_date: Optional[str] = None
    user_id: str
    created_at: str


class TaskUpdatedPayload(BaseModel):
    """Payload for task.updated event"""
    id: str
    changes: Dict[str, Any]
    updated_at: str


class TaskCompletedPayload(BaseModel):
    """Payload for task.completed event"""
    id: str
    completed_at: str
    is_completed: bool = True


class TaskDeletedPayload(BaseModel):
    """Payload for task.deleted event"""
    id: str
    deleted_at: str


# Reminder event payloads
class ReminderSentPayload(BaseModel):
    """Payload for task.reminder_sent event"""
    reminder_id: str
    task_id: str
    delivery_channel: str
    sent_at: str


# Recurring task event payloads
class RecurringInstanceGeneratedPayload(BaseModel):
    """Payload for recurring.instance_generated event"""
    recurring_task_id: str
    new_task_id: str
    due_date: str
    generated_at: str


# Event type constants
class EventTypes:
    """Constants for event types"""
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"
    REMINDER_SENT = "task.reminder_sent"
    RECURRING_INSTANCE_GENERATED = "recurring.instance_generated"
    
    ALL_TYPES = [
        TASK_CREATED,
        TASK_UPDATED,
        TASK_COMPLETED,
        TASK_DELETED,
        REMINDER_SENT,
        RECURRING_INSTANCE_GENERATED,
    ]


# Kafka topic constants
class KafkaTopics:
    """Constants for Kafka topics"""
    TASKS_CREATED = "todo.tasks.created"
    TASKS_UPDATED = "todo.tasks.updated"
    TASKS_COMPLETED = "todo.tasks.completed"
    TASKS_DELETED = "todo.tasks.deleted"
    REMINDERS = "todo.reminders"
    RECURRING = "todo.recurring"
    ALL_EVENTS = "todo-events"  # Main topic for all events
