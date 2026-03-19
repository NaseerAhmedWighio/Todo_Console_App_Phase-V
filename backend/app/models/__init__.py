# Models package - export all models

from .conversation import Conversation
from .email_verification import EmailVerification
from .event import DomainEvent, DomainEventBase, DomainEventCreate, DomainEventResponse
from .message import Message
from .recurring_task import (
    RecurringTask,
    RecurringTaskBase,
    RecurringTaskCreate,
    RecurringTaskResponse,
    RecurringTaskUpdate,
)
from .reminder import Reminder, ReminderBase, ReminderCreate, ReminderResponse, ReminderUpdate

# Advanced todo features models
from .tag import Tag, TagBase, TagCreate, TagResponse, TagUpdate
from .task_tag import TaskTag
from .todo import Todo, TodoBase, TodoCreate, TodoResponse, TodoUpdate
from .user import User, UserCreate, UserResponse, UserUpdate, get_utc_now, hash_password, verify_password

__all__ = [
    # User models
    "User",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "hash_password",
    "verify_password",
    "get_utc_now",
    # Email verification
    "EmailVerification",
    # Todo models
    "Todo",
    "TodoBase",
    "TodoCreate",
    "TodoUpdate",
    "TodoResponse",
    # Chat models
    "Message",
    "Conversation",
    # Tag models
    "Tag",
    "TagBase",
    "TagCreate",
    "TagUpdate",
    "TagResponse",
    # TaskTag model
    "TaskTag",
    # Reminder models
    "Reminder",
    "ReminderBase",
    "ReminderCreate",
    "ReminderUpdate",
    "ReminderResponse",
    # RecurringTask models
    "RecurringTask",
    "RecurringTaskBase",
    "RecurringTaskCreate",
    "RecurringTaskUpdate",
    "RecurringTaskResponse",
    # Event models
    "DomainEvent",
    "DomainEventBase",
    "DomainEventCreate",
    "DomainEventResponse",
]
