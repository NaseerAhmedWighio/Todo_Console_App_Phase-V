# Models package - export all models

from .user import User, UserCreate, UserUpdate, UserResponse, hash_password, verify_password, get_utc_now
from .todo import Todo, TodoBase, TodoCreate, TodoUpdate, TodoResponse
from .message import Message
from .conversation import Conversation
from .email_verification import EmailVerification

# Advanced todo features models
from .tag import Tag, TagBase, TagCreate, TagUpdate, TagResponse
from .task_tag import TaskTag
from .reminder import Reminder, ReminderBase, ReminderCreate, ReminderUpdate, ReminderResponse
from .recurring_task import RecurringTask, RecurringTaskBase, RecurringTaskCreate, RecurringTaskUpdate, RecurringTaskResponse
from .event import DomainEvent, DomainEventBase, DomainEventCreate, DomainEventResponse

__all__ = [
    # User models
    "User", "UserCreate", "UserUpdate", "UserResponse", "hash_password", "verify_password", "get_utc_now",
    # Email verification
    "EmailVerification",
    # Todo models
    "Todo", "TodoBase", "TodoCreate", "TodoUpdate", "TodoResponse",
    # Chat models
    "Message", "Conversation",
    # Tag models
    "Tag", "TagBase", "TagCreate", "TagUpdate", "TagResponse",
    # TaskTag model
    "TaskTag",
    # Reminder models
    "Reminder", "ReminderBase", "ReminderCreate", "ReminderUpdate", "ReminderResponse",
    # RecurringTask models
    "RecurringTask", "RecurringTaskBase", "RecurringTaskCreate", "RecurringTaskUpdate", "RecurringTaskResponse",
    # Event models
    "DomainEvent", "DomainEventBase", "DomainEventCreate", "DomainEventResponse",
]
