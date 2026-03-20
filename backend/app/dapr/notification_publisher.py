"""
Dapr Notification Publisher
Publishes notification events to Dapr pub/sub for scheduled and recurring notifications
"""

import logging
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ..dapr.pubsub import DaprPubSub
from ..models.todo import Todo
from ..models.user import User

logger = logging.getLogger(__name__)


class NotificationPublisher:
    """Publisher for notification events via Dapr pub/sub"""

    def __init__(self):
        self.pubsub = DaprPubSub()

    def publish_scheduled_notification(
        self,
        todo: Todo,
        user: User,
        scheduled_time: datetime,
    ) -> bool:
        """
        Publish a scheduled notification event

        Args:
            todo: The todo item
            user: The user who owns the task
            scheduled_time: When the notification should be sent

        Returns:
            True if published successfully
        """
        try:
            event = {
                "type": "scheduled_notification",
                "todo_id": str(todo.id),
                "user_id": str(user.id),
                "user_email": user.email,
                "user_name": user.name or user.email.split("@")[0],
                "task_title": todo.title,
                "task_description": todo.description,
                "scheduled_time": scheduled_time.isoformat(),
                "due_date": todo.due_date.isoformat() if todo.due_date else None,
                "priority": todo.priority or "medium",
                "timezone": user.timezone or "UTC",
            }

            # Publish to Dapr pub/sub
            self.pubsub.publish(
                pubsub_name="notification-pubsub",
                topic="notifications",
                data=event,
            )

            logger.info(
                f"Published scheduled notification event for task {todo.id} to user {user.email}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to publish scheduled notification event: {str(e)}")
            return False

    def publish_recurring_notification(
        self,
        todo: Todo,
        user: User,
        recurring_task_id: str,
        pattern: str,
        occurrence_number: int = 1,
    ) -> bool:
        """
        Publish a recurring notification event

        Args:
            todo: The todo item
            user: The user who owns the task
            recurring_task_id: ID of the recurring task configuration
            pattern: Recurrence pattern (daily, weekly, monthly, pay_bills, etc.)
            occurrence_number: Which occurrence this is

        Returns:
            True if published successfully
        """
        try:
            event = {
                "type": "recurring_notification",
                "todo_id": str(todo.id),
                "user_id": str(user.id),
                "user_email": user.email,
                "user_name": user.name or user.email.split("@")[0],
                "task_title": todo.title,
                "task_description": todo.description,
                "recurring_task_id": str(recurring_task_id),
                "pattern": pattern,
                "occurrence_number": occurrence_number,
                "due_date": todo.due_date.isoformat() if todo.due_date else None,
                "scheduled_time": todo.scheduled_time.isoformat() if todo.scheduled_time else None,
                "priority": todo.priority or "medium",
                "timezone": user.timezone or "UTC",
            }

            # Publish to Dapr pub/sub
            self.pubsub.publish(
                pubsub_name="notification-pubsub",
                topic="notifications",
                data=event,
            )

            logger.info(
                f"Published recurring notification event for task {todo.id} (pattern: {pattern})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to publish recurring notification event: {str(e)}")
            return False

    def publish_reminder_created(
        self,
        todo: Todo,
        user: User,
        reminder_time: datetime,
    ) -> bool:
        """
        Publish a reminder created event (for immediate scheduling)

        Args:
            todo: The todo item
            user: The user who owns the task
            reminder_time: When the reminder should trigger

        Returns:
            True if published successfully
        """
        try:
            event = {
                "type": "reminder_created",
                "todo_id": str(todo.id),
                "user_id": str(user.id),
                "user_email": user.email,
                "reminder_time": reminder_time.isoformat(),
                "task_title": todo.title,
                "timezone": user.timezone or "UTC",
            }

            self.pubsub.publish(
                pubsub_name="notification-pubsub",
                topic="notifications",
                data=event,
            )

            logger.info(f"Published reminder created event for task {todo.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to publish reminder created event: {str(e)}")
            return False


# Singleton instance
notification_publisher = NotificationPublisher()
